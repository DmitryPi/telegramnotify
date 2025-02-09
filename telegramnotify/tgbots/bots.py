import asyncio
import decimal
import html
import json
import logging
import re
import traceback
import warnings

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime
from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    LabeledPrice,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)
from telegram.warnings import PTBUserWarning

from config.settings.base import (
    DEBUG,
    TELEGRAM_ADMIN_ID,
    TELEGRAM_API_TOKEN,
    YOKASSA_TOKEN,
)
from telegramnotify.core.models import Order, Service
from telegramnotify.parsers.models import ParserEntry
from telegramnotify.tickets.models import Ticket
from telegramnotify.utils.orm import (
    get_parser_entries,
    get_users_exclude_expired,
    update_parser_entries_sent,
)
from telegramnotify.utils.other import (
    datetime_days_ahead,
    list_into_chunks,
    search_word,
)

User = get_user_model()

AUTH_CHOOSE_SERVICE, AUTH_SET_WORDS, AUTH_CONFIRM_WORDS = map(chr, range(3))
PAYMENT_BUILD_INVOICE = map(chr, range(3, 4))
SETTINGS_CHOOSE, ADD_SERVICE, REMOVE_SERVICE, ADD_WORDS, REMOVE_WORD = map(
    chr, range(4, 9)
)
SEND_TECHSUPPORT_MSG = map(chr, range(9, 10))
END = ConversationHandler.END

warnings.filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)


class SenderBot:
    def __init__(self):
        self.bot = Bot(TELEGRAM_API_TOKEN)

    async def raw_send_message(self, chat_id, msg) -> None:
        """Raw api send_message: asyncio.run(self.raw_send_message())"""
        try:
            async with self.bot as bot:
                await bot.send_message(
                    chat_id,
                    msg,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                    protect_content=True,
                )
        except BadRequest:
            print(f"Chat {chat_id} was not found. Message was not sent.")

    @property
    def premium_expired_message(self) -> str:
        message = "🔴 Срок премиума истёк."
        return message

    def build_reply_message(self, ticket: Ticket) -> str:
        """Build html reply message for telegram user"""
        msg = "".join(
            [
                "@admin: ",
                ticket.reply,
            ]
        )
        return msg

    def build_entry_message(self, entry: ParserEntry) -> str:
        """Build html message for telegram user"""
        description = (
            f"{entry.description[:300].strip()}..."
            if len(entry.description) > 300
            else entry.description
        )
        msg = "".join(
            [
                f"<b>{entry.title}</b>",
                f"<pre>Бюджет: {entry.budget}</pre>",
                f"<pre>Срок: {entry.deadline}</>",
                f"<a href='{entry.url}'>{description}</a>",
            ]
        )
        return msg

    def search_words(self, user: User, entry: ParserEntry) -> re.Match:
        """Build text - concat entry.title, entry.description
        Loop through entry.words and search_word in text
        return re.Match if any
        """
        text = entry.title + " " + entry.description
        for word in user.words:
            match = search_word(text, word)
            if match:
                return match

    def run(self) -> None:
        """
        get entries with sent=False
        get users
        Loop through users and entries
        If theres match on user words
        => send message to telegram user
        """
        entries = get_parser_entries()
        users = get_users_exclude_expired()

        if not entries:
            return None

        for user in users:
            for entry in entries:
                # search user words on particular entry
                match = self.search_words(user, entry)
                if not match:
                    continue
                # if there's match
                message = self.build_entry_message(entry)
                asyncio.run(self.raw_send_message(user.tg_id, message))
        # update entries set sent=True
        update_parser_entries_sent(entries)


class TelegramBot:
    def __init__(self):
        self.services = []
        self.settings = [
            "Добавить сервис",
            "Удалить сервис",
            "Добавить слова",
            "Удалить слово",
        ]
        self.yesno = ["Да", "Нет"]
        self.commands = {
            "start": "/start",
            "help": "/help",
            "pay": "/pay",
            "account": "/account",
            "settings": "/settings",
            "techsupport": "/support",
            "cancel": "/cancel",
        }
        self.set_services()

    def set_services(self):
        """GET all Service objects and update self.services"""
        services = Service.objects.all()
        self.services = [service.title for service in services]

    @property
    def auth_invalid_msg(self) -> str:
        return (
            f"🔴 Пройдите регистрацию.\n\nИспользуйте команду - {self.commands['start']}"
        )

    @property
    def error_msg(self) -> str:
        return "🔴 Ой, что-то пошло не так.\n\nПрограммист оповещен об этом!"

    def build_keyboard(self, buttons: list[str]) -> list[KeyboardButton]:
        """
        Suggestion keyboard:
        {
            'keyboard': [[{'text': 100}, {'text': 200}]]
        }
        """
        btns = [[KeyboardButton(s, callback_data=s) for s in buttons]]
        reply_markup = ReplyKeyboardMarkup(btns)
        return reply_markup

    def build_inline_keyboard(self, buttons: list[str], grid=2) -> InlineKeyboardMarkup:
        """
        Chat reply keyboard:
        {
            'inline_keyboard': [
                [
                    {'callback_data': 'Добавить сервис', 'text': 'Добавить сервис'},
                    {'callback_data': 'Добавить слова', 'text': 'Добавить слова'},
                    {'callback_data': 'Удалить сервис', 'text': 'Удалить сервис'},
                    {'callback_data': 'Удалить слово', 'text': 'Удалить слово'}
                ]
            ]
        }
        """
        btns = [InlineKeyboardButton(s, callback_data=s) for s in buttons]
        btns = list_into_chunks(btns, n=grid)
        reply_markup = InlineKeyboardMarkup(btns)
        return reply_markup

    async def command_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        try:
            await User.objects.aget(tg_id=update.effective_user.id)
            msg = "\n".join(
                [
                    "Вы уже зарегистрированы",
                ]
            )
            await update.message.reply_text(msg)
        except User.DoesNotExist:
            msg = "\n".join(
                [
                    "Привет!\n",
                    "Я могу оповещать Вас о новых заказах и проектах",
                    "\n<b>Выберите сервис:</b>",
                ]
            )
            await sync_to_async(self.set_services)()
            reply_markup = self.build_inline_keyboard(self.services)
            await update.message.reply_text(
                msg, reply_markup=reply_markup, parse_mode=ParseMode.HTML
            )
            return AUTH_CHOOSE_SERVICE

    async def auth_service(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Выбор сервиса для поиска"""
        query = update.callback_query
        await query.answer()
        context.user_data.update({"service": query.data})
        msg = "\n".join(
            [
                "Вы выбрали - " + query.data,
                "" "\n<b>→ Теперь введите несколько фраз-слов для поиска</b>\n",
                "● Вы можете ввести сразу несколько слов, через запятую",
                "● Максимальная длина слова - 50 символов",
                "● Минимальная длина слова - 2 символа",
                "● В пробном периоде доступно до 5 фраз-слов\n",
                "<b>Пример</b>: парсинг, дизайн страницы, api, верстка, полиграфия",
                f"\n<b>Отмена регистрации</b> - {self.commands['cancel']}",
            ]
        )
        await query.edit_message_text(text=msg, parse_mode=ParseMode.HTML)
        return AUTH_SET_WORDS

    async def _validate_words(self, words: str, word_limit=5) -> list[str] | None:
        """Обработать, очистить слова поиска пользователя

        Args:
            words (str): Слова пользователя, через запятую
            word_limit (int, optional): Ограничение слов. Defaults to 5.

        Returns:
            list[str] | None: Список слов без пробелов, меньше 50 символов, больше 2
        """
        word_list = words.split(",")[:word_limit]
        word_list = [w.strip().lower() for w in word_list if len(w) < 50 and len(w) > 2]
        return word_list

    async def auth_words(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Обработка слов"""
        words = await self._validate_words(update.message.text)

        if not words:
            msg = "<b>🔴 Слова не подходят или отсутствуют</b>"
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
            return AUTH_SET_WORDS

        context.user_data.update({"words": words})
        msg = "\n".join(
            [
                "Ваши слова для поиска:\n",
                str(words),
                "\n<b>Подтверждаете?</b>",
            ]
        )
        reply_markup = self.build_inline_keyboard(self.yesno)
        await update.message.reply_text(
            msg, reply_markup=reply_markup, parse_mode=ParseMode.HTML
        )
        return AUTH_CONFIRM_WORDS

    async def auth_words_confirm(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Подтверждение введенных пользователем слов"""
        query = update.callback_query
        await query.answer()
        answer = query.data
        if answer == "Да":
            msg = "\n".join(
                [
                    "<b>Спасибо за регистрацию!</b>",
                    "",
                    "● Вы находитесь в пробном периоде",
                    "● Вы можете продлить работу сервиса и расширить функционал",
                    "",
                    "<b>Помошник команд - </b>" + self.commands["help"],
                    "<b>Тех.поддержка - </b>" + self.commands["techsupport"],
                    "<b>Настройки - </b>" + self.commands["settings"],
                    "",
                    "<b>Личный кабинет - </b>" + self.commands["account"],
                    "<b>Пополните баланс - </b>" + self.commands["pay"],
                ]
            )
            # authenticate
            await self.auth_complete(update, context)
            await query.edit_message_text(text=msg, parse_mode=ParseMode.HTML)
            return END
        else:
            msg = "<b>Введите новые слова:</b>"
            await query.edit_message_text(text=msg, parse_mode=ParseMode.HTML)
            return AUTH_SET_WORDS

    async def auth_complete(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Регистрация пользователя в django-приложении

        TODO: acreate to create_user
        """
        tg_user = update.effective_user
        username = tg_user.username if tg_user.username else tg_user.first_name
        service = await Service.objects.aget(title=context.user_data["service"])
        user = await User.objects.acreate(
            tg_id=tg_user.id,
            username=username,
            password=str(tg_user.id),
            name=tg_user.first_name,
            words=context.user_data["words"],
            pay_rate=0,
            wallet=0,
            premium_status=User.PremiumStatus.trial,
            premium_expire=datetime_days_ahead(3),
        )
        await sync_to_async(user.services.add)(service)

    async def command_pay(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        try:
            await User.objects.aget(tg_id=update.effective_user.id)
            msg = "\n".join(
                [
                    "<b>Введите желаемое количество для пополнения</b>",
                    "",
                    "● Минимальное количество - 100 рублей.",
                    "",
                    "Отмена операции - /cancel",
                ]
            )
            reply_markup = self.build_keyboard([100, 200, 300, 400, 500])
            await update.message.reply_text(
                msg, reply_markup=reply_markup, parse_mode=ParseMode.HTML
            )
            return PAYMENT_BUILD_INVOICE
        except User.DoesNotExist:
            await update.message.reply_text(self.auth_invalid_msg)

    async def build_invoice(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        try:
            pay_amount = int(update.message.text)
            if pay_amount < 100:
                raise ValueError
        except (ValueError, AttributeError):
            msg = "\n".join(
                [
                    "🔴 <b>Неверное количество!</b>",
                    "",
                    "● Минимальное количество - 100 рублей.",
                    "",
                    "Отмена операции - /cancel",
                ]
            )
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
            return PAYMENT_BUILD_INVOICE
        chat_id = update.message.chat_id
        title = "Пополнение баланса:"
        description = "-"
        payload = "Secret-Payload"
        provider_token = YOKASSA_TOKEN
        currency = "RUB"
        prices = [LabeledPrice("Test", pay_amount * 100)]
        await update.message.reply_text("●", reply_markup=ReplyKeyboardRemove())
        await context.bot.send_invoice(
            chat_id,
            title,
            description,
            payload,
            provider_token,
            currency,
            prices,
        )
        return END

    async def precheckout_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Answers the PreQecheckoutQuery"""
        query = update.pre_checkout_query
        # check the payload, is this from your bot?
        if query.invoice_payload != "Secret-Payload":
            # answer False pre_checkout_query
            await query.answer(ok=False, error_message="🔴 Что-то пошло не так...")
        else:
            await query.answer(ok=True)

    async def successful_payment_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Confirms the successful payment.
        TEST CARD: 1111 1111 1111 1026, 12/22, CVC 000.
            ORDER: {
             'invoice_payload': 'Secret-Payload',
             'currency': 'RUB',
             'order_info': {},
             'telegram_payment_charge_id': '5432524_519367_706459',
             'provider_payment_charge_id': '2af0afbc-0000-198bce8',
             'total_amount': 10000
            }
        TODO: more tests (scenarios: small/big/random number, multiple payments)
        TODO: decouple
        """
        user = await User.objects.aget(tg_id=update.effective_user.id)
        order = update.message.successful_payment
        amount = decimal.Decimal(order["total_amount"] / 100)
        msg = "\n".join(
            [
                "🙏 <b>Дай бог здоровья!</b>",
                "",
                f"Счет пополнен на {amount} рублей",
                "",
                "<b>Вывести баланс - </b>" + self.commands["account"],
            ]
        )
        # wallet update
        await sync_to_async(user.update_wallet)(amount)
        # save order info
        await Order.objects.acreate(
            user=user,
            status=Order.Status.SUCCESS,
            invoice_payload=order["invoice_payload"],
            currency=order["currency"],
            total_amount=amount,
            telegram_payment_charge_id=order["telegram_payment_charge_id"],
            provider_payment_charge_id=order["provider_payment_charge_id"],
        )
        # send success msg
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

    async def command_account(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        TODO: улучшить оформление вывода 'Сервисы' и 'Слова поиска'
        """
        try:
            user = await User.objects.prefetch_related("services").aget(
                tg_id=update.effective_user.id
            )
            services = [s.__str__() for s in user.services.all()]
            premium_expire = localtime(user.premium_expire).strftime(
                "%d-%m-%Y %H:%M:%S"
            )
            msg = "\n".join(
                [
                    f"<pre>ID: {user.tg_id}</pre>",
                    "",
                    f"<b>Ваш баланс</b>: {user.wallet} рублей",
                    "",
                    f"<b>Тарифный план</b>: {user.premium_status.capitalize()}",
                    f"<b>Действует до: {premium_expire}</b>",
                    "",
                    f"<b>Сервисы:</b> {services}",
                    f"<b>Слова поиска:</b> {user.words}",
                    "",
                    f"<b>Потребление в день:</b> {user.pay_rate} рубля",
                    f"<b>Потребление в месяц:</b> {user.pay_rate * 30} рублей",
                ]
            )
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
        except User.DoesNotExist:
            await update.message.reply_text(self.auth_invalid_msg)

    async def command_settings(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """
        Добавление сервис / Добавить слова
        Удалить сервис / Удалить слово
        Отключение/Включение работы

        TODO: button logic
        """
        try:
            user = await User.objects.prefetch_related("services").aget(
                tg_id=update.effective_user.id
            )
            context.user_data.update({"user": user})
            reply_markup = self.build_inline_keyboard(self.settings, grid=2)
            msg = "<b>Настройки: /cancel</b>"
            await update.message.reply_text(
                msg, reply_markup=reply_markup, parse_mode=ParseMode.HTML
            )
            return SETTINGS_CHOOSE
        except User.DoesNotExist:
            await update.message.reply_text(self.auth_invalid_msg)

    async def settings_choose(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        query = update.callback_query
        await query.answer()
        answer = query.data
        user = context.user_data["user"]
        user_services = user.services.all()
        user_services_title = [s.title for s in user_services]
        # update services
        await sync_to_async(self.set_services)()
        # choices
        match answer:
            case "Добавить сервис":
                """
                TODO: динамика кнопок - сервисы - юзер сервисы
                """
                reply_markup = self.build_inline_keyboard(self.services)
                await query.edit_message_text(text=answer, reply_markup=reply_markup)
                return ADD_SERVICE
            case "Удалить сервис":
                if not user_services:
                    await query.edit_message_text(
                        text="<b>Сервисы отсутствуют</b>", parse_mode=ParseMode.HTML
                    )
                    return END
                reply_markup = self.build_inline_keyboard(user_services_title)
                await query.edit_message_text(text=answer, reply_markup=reply_markup)
                return REMOVE_SERVICE
            case "Добавить слова":
                await query.edit_message_text(text=answer, parse_mode=ParseMode.HTML)
                return ADD_WORDS
            case "Удалить слово":
                if not user.words:
                    await query.edit_message_text(
                        text="<b>Слова отсутствуют</b>", parse_mode=ParseMode.HTML
                    )
                    return END
                reply_markup = self.build_inline_keyboard(user.words)
                await query.edit_message_text(text=answer, reply_markup=reply_markup)
                return REMOVE_WORD

    def _user_add_service(self, user: User, service: str) -> None:
        """
        TODO: Добавить списание средств за 1 календарный день, обновление статуса
        """
        service = Service.objects.get(title=service)
        # user_services = user.services.all()
        # if service in user_services:
        #     pass
        # else:
        user.services.add(service)
        user.save()

    def _user_remove_service(self, user: User, service: str) -> None:
        service = Service.objects.get(title=service)
        user.services.remove(service)
        user.save()

    def _user_add_words(self, user: User, words: list[str]) -> None:
        user.words += words
        user.save()

    def _user_remove_word(self, user: User, word: str) -> None:
        user.words.remove(word)
        user.save()

    async def option_add_service(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        query = update.callback_query
        await query.answer()
        answer = query.data
        # add user service
        user = context.user_data["user"]
        await sync_to_async(self._user_add_service)(user, answer)
        await query.edit_message_text(text="Сервис добавлен")
        return END

    async def option_remove_service(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        query = update.callback_query
        await query.answer()
        answer = query.data
        # Remove user service
        user = context.user_data["user"]
        await sync_to_async(self._user_remove_service)(user, answer)
        await query.edit_message_text(text="Сервис удалён")
        return END

    async def option_add_words(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        user = context.user_data["user"]
        words = await self._validate_words(update.message.text)

        if not words:
            msg = "<b>🔴 Слова не подходят или отсутствуют</b>"
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
            return ADD_WORDS
        else:
            await sync_to_async(self._user_add_words)(user, words)

        msg = "<b>Слова обновлены!</b>"
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
        return END

    async def option_remove_word(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        query = update.callback_query
        await query.answer()
        answer = query.data
        # Update user words
        user = context.user_data["user"]
        await sync_to_async(self._user_remove_word)(user, answer)
        await query.edit_message_text(text="Слово удалено")
        return END

    async def command_techsupport(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        try:
            await User.objects.aget(tg_id=update.effective_user.id)
            msg = "<b>Задайте вопрос:</b>\nДля отмены - /cancel"
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
            return SEND_TECHSUPPORT_MSG
        except User.DoesNotExist:
            await update.message.reply_text(self.auth_invalid_msg)

    async def techsupport_msg(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Create support Ticket"""
        try:
            user = await User.objects.aget(tg_id=update.effective_user.id)
            msg = "<b>Вопрос отправлен!</b>"
            # save Ticket
            await Ticket.objects.acreate(
                user=user,
                message=str(update.message.text),
                status=Ticket.Status.UNSOLVED,
            )
            # send succes msg
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
            return END
        except IndexError:
            await update.message.reply_text(self.auth_invalid_msg)
            return END

    async def command_help(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        try:
            await User.objects.aget(tg_id=update.effective_user.id)
            msg = "\n".join(
                [
                    "<b>Доступные команды:</b>",
                    "",
                    f"{self.commands['account']} - Баланс и Личный кабинет",
                    f"{self.commands['pay']} - Пополнить баланс",
                    f"{self.commands['settings']} - Настройки",
                    f"{self.commands['techsupport']} - Техническая поддержка",
                ]
            )
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
        except User.DoesNotExist:
            await update.message.reply_text(self.auth_invalid_msg)

    async def command_cancel_conv(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Cancels and ends the conversation."""
        msg = "Операция прервана"
        await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
        return END

    async def error_handler(
        self, update: object, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Log the error and send a telegram message to notify the developer."""
        # Log the error before we do anything else, so we can see it even if something breaks.
        logging.error(
            msg="\n\nException while handling an update:", exc_info=context.error
        )

        # traceback.format_exception returns the usual python message about an exception, but as a
        # list of strings rather than a single string, so we have to join them together.
        tb_list = traceback.format_exception(
            None, context.error, context.error.__traceback__
        )
        tb_string = "".join(tb_list)

        # Build the message with some markup and additional information about what happened.
        # You might need to add some logic to deal with messages longer than the 4096 character limit.
        update_str = update.to_dict() if isinstance(update, Update) else str(update)
        message = (
            f"An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
            "</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )

        # Finally, send the message
        await context.bot.send_message(
            chat_id=TELEGRAM_ADMIN_ID,
            text=message,
            parse_mode=ParseMode.HTML,
        )

    def run(self):
        """Run telegram bot instance"""
        # Create the Application and pass it your bot's token.
        application = Application.builder().token(TELEGRAM_API_TOKEN).build()
        # conversations
        start_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.command_start)],
            states={
                AUTH_CHOOSE_SERVICE: [CallbackQueryHandler(self.auth_service)],
                AUTH_SET_WORDS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.auth_words)
                ],
                AUTH_CONFIRM_WORDS: [CallbackQueryHandler(self.auth_words_confirm)],
            },
            fallbacks=[CommandHandler("cancel", self.command_cancel_conv)],
        )
        pay_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("pay", self.command_pay)],
            states={
                PAYMENT_BUILD_INVOICE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.build_invoice)
                ]
            },
            fallbacks=[CommandHandler("cancel", self.command_cancel_conv)],
        )
        settings_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("settings", self.command_settings)],
            states={
                SETTINGS_CHOOSE: [CallbackQueryHandler(self.settings_choose)],
                ADD_SERVICE: [CallbackQueryHandler(self.option_add_service)],
                REMOVE_SERVICE: [CallbackQueryHandler(self.option_remove_service)],
                ADD_WORDS: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.option_add_words
                    )
                ],
                REMOVE_WORD: [CallbackQueryHandler(self.option_remove_word)],
            },
            fallbacks=[CommandHandler("cancel", self.command_cancel_conv)],
        )
        techsupport_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("support", self.command_techsupport)],
            states={
                SEND_TECHSUPPORT_MSG: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.techsupport_msg
                    )
                ]
            },
            fallbacks=[CommandHandler("cancel", self.command_cancel_conv)],
        )
        # generic handlers
        application.add_handler(start_conv_handler)
        application.add_handler(settings_conv_handler)
        application.add_handler(techsupport_conv_handler)
        application.add_handler(CommandHandler("account", self.command_account))
        application.add_handler(CommandHandler("help", self.command_help))
        # payments
        application.add_handler(pay_conv_handler)
        application.add_handler(PreCheckoutQueryHandler(self.precheckout_callback))
        application.add_handler(
            MessageHandler(filters.SUCCESSFUL_PAYMENT, self.successful_payment_callback)
        )
        #  error handler
        if not DEBUG:
            application.add_error_handler(self.error_handler)
        # Run the bot until the user presses Ctrl-C
        application.run_polling()
