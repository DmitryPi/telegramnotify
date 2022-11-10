import asyncio  # noqa isort:skip
import html
import json
import logging
import traceback

from environ import Env
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    LabeledPrice,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode
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

ONE, TWO, THREE, FOUR = (i for i in range(1, 5))


class SenderBot:
    pass


class TelegramBot:
    def __init__(self, env: Env):
        self.env = env
        self.api_token = self.env("TELEGRAM_API_TOKEN")
        self.db = ""
        self.db_conn = ""
        self.services = ["FL.ru", "avito"]
        self.settings = [
            "Добавить сервис",
            "Добавить слова",
            "Удалить сервис",
            "Удалить слово",
        ]
        self.yesno = ["Да", "Нет"]
        self.commands = {
            "start": "/start",
            "help": "/help",
            "pay": "/pay",
            "balance": "/balance",
            "bill": "/bill",
            "settings": "/settings",
            "techsupport": "/techsupport",
            "cancel": "/cancel",
        }

    @property
    def auth_invalid_msg(self) -> str:
        return f"Пройдите регистрацию.\nИспользуйте команду - {self.commands['start']}"

    def build_keyboard(self, context: list[str]) -> list[KeyboardButton]:
        btns = [KeyboardButton(s, callback_data=s) for s in context]
        reply_markup = ReplyKeyboardMarkup([btns])
        return reply_markup

    def build_inline_keyboard(self, context: list[str], grid=2) -> InlineKeyboardMarkup:
        """TODO: btn grid division"""
        btns = [[InlineKeyboardButton(s, callback_data=s) for s in context]]
        reply_markup = InlineKeyboardMarkup(btns)
        return reply_markup

    async def command_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        try:
            self.db.get_user(self.db_conn, update.effective_user.id)
            msg = "\n".join(
                [
                    "Вы уже зарегистрированы",
                ]
            )
            await update.message.reply_text(msg)
        except IndexError:
            msg = "\n".join(
                [
                    "Привет!",
                    "Я могу оповещать тебя о новых заказах и проектах",
                    "\n<b>Выбери сервис:</b>",
                ]
            )
            reply_markup = self.build_inline_keyboard(self.services)
            await update.message.reply_text(
                msg, reply_markup=reply_markup, parse_mode=ParseMode.HTML
            )
            return ONE

    async def auth_service(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Выбор сервиса для поиска"""
        query = update.callback_query
        await query.answer()
        context.user_data.update({"service": query.data.split(" ")})
        msg = "\n".join(
            [
                "Вы выбрали - " + query.data,
                "\nВведи несколько фраз-слов для поиска.\n",
                "*Вы можете ввести сразу несколько слов, через запятую*",
                "*Минимальная длина слова - 3 символа*",
                "*В пробном периоде доступно до 5 слов-фраз*",
                f"\nОтмена операции - {self.commands['cancel']}\n",
                "<b>Пример</b>: парсинг, дизайн страницы, бот, верстка, написать на питоне",
            ]
        )
        await query.edit_message_text(text=msg, parse_mode=ParseMode.HTML)
        return TWO

    async def auth_words(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """TODO: очистка слов от всего плохого"""
        words = update.message.text.split(",")[:5]  # only 5 words allowed
        words = [w.strip() for w in words]
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
        return THREE

    async def auth_words_confirm(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Подтверждение введенных пользователем слов"""
        query = update.callback_query
        await query.answer()
        answer = query.data
        if answer == "Да":
            user_service = context.user_data["service"][0]
            user_words = str(context.user_data["words"])
            msg = "\n".join(
                [
                    "Спасибо за регистрацию!\n",
                    "Вы выбрали сервис: " + user_service,
                    "Слова для поиска: " + user_words,
                    "\nВы находитесь в пробном периоде.",
                    "Чтобы продлить период работы, пополните баланс",
                    "Вызвав команду - " + self.commands["pay"],
                ]
            )
            await query.edit_message_text(text=msg)
            await self.auth_complete(update, context)
            return ConversationHandler.END
        else:
            msg = "<b>Введите новые слова:</b>"
            await query.edit_message_text(text=msg, parse_mode=ParseMode.HTML)
            return TWO

    async def auth_complete(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        user = build_user(update.effective_user, context.user_data)  # noqa skip
        self.db.insert_user(self.db_conn, user)

    async def command_pay(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        try:
            self.db.get_user(self.db_conn, update.effective_user.id)
            msg = "\n".join(
                [
                    "Введите желаемое количество для пополнения.",
                    "Минимальное сумма пополнения - 100 рублей.",
                ]
            )
            reply_markup = self.build_keyboard([100, 200, 300, 400, 500])
            await update.message.reply_text(msg, reply_markup=reply_markup)
            return ONE
        except IndexError:
            await update.message.reply_text(self.auth_invalid_msg)

    async def build_invoice(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        try:
            pay_amount = int(update.message.text)
            if pay_amount < 100:
                raise ValueError
        except ValueError:
            msg = "\n".join(
                [
                    "<b>Неверное количество!</b>",
                    "Минимальное сумма пополнения - 100 рублей.",
                    "\nДля отмены - /cancel",
                ]
            )
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
            return ONE
        chat_id = update.message.chat_id
        title = "Пополнение баланса:"
        description = "Описание услуги"
        payload = "Secret-Payload"
        provider_token = self.env["YOKASSA_TOKEN"]
        currency = "RUB"
        prices = [LabeledPrice("Test", pay_amount * 100)]
        await update.message.reply_text(".", reply_markup=ReplyKeyboardRemove())
        await context.bot.send_invoice(
            chat_id,
            title,
            description,
            payload,
            provider_token,
            currency,
            prices,
        )
        return ConversationHandler.END

    async def precheckout_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Answers the PreQecheckoutQuery"""
        query = update.pre_checkout_query
        # check the payload, is this from your bot?
        if query.invoice_payload != "Secret-Payload":
            # answer False pre_checkout_query
            await query.answer(ok=False, error_message="Что-то пошло не так...")
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
         'telegram_payment_charge_id': '5432524_519367_706459', 'provider_payment_charge_id': '2af0afbc-0000-198bce8',
         'total_amount': 10000}
        TODO: save order info
        """
        user_id = update.effective_user["id"]
        order = update.message.successful_payment
        amount = order["total_amount"] / 100
        msg = "\n".join(
            [
                "Спасибо! Оплата прошла успешно.",
                "Вывести ваш баланс - " + self.commands["balance"],
            ]
        )
        self.db.update_user_wallet(self.db_conn, user_id, amount)
        await update.message.reply_text(msg)

    async def command_balance(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        try:
            user = self.db.get_user(self.db_conn, update.effective_user.id)
            msg = f"<b>Ваш баланс</b>: {user.wallet} рублей"
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
        except IndexError:
            await update.message.reply_text(self.auth_invalid_msg)

    async def command_bill(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        try:
            user = self.db.get_user(self.db_conn, update.effective_user.id)
            msg = "\n".join(
                [
                    f"<b>Тарифный план</b>: {user.premium_status}",
                    f"<b>Потребление в день</b>: {user.bill} рубля",
                    f"<b>Потребление в месяц</b>: {user.bill * 30} рублей",
                ]
            )
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
        except IndexError:
            await update.message.reply_text(self.auth_invalid_msg)

    async def command_settings(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """
        Добавление сервис / Добавить слова
        Удалить сервис / Удалить слово
        Отключение/Включение работы
        """
        try:
            user = self.db.get_user(self.db_conn, update.effective_user.id)
            context.user_data.update({"user": user})
            reply_markup = self.build_inline_keyboard(self.settings)
            msg = "<b>Настройки:</b>"
            await update.message.reply_text(
                msg, reply_markup=reply_markup, parse_mode=ParseMode.HTML
            )
            return ConversationHandler.END
        except IndexError:
            await update.message.reply_text(self.auth_invalid_msg)

    async def settings_choose(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        user = context.user_data["user"]
        query = update.callback_query
        await query.answer()
        answer = query.data
        if answer == self.settings[0]:  # Сервисы
            reply_markup = self.build_inline_keyboard(self.services)
            await query.edit_message_text(text=answer, reply_markup=reply_markup)
            return TWO
        elif answer == self.settings[1]:  # Слова
            user_words = json.loads(user.words)
            reply_markup = self.build_inline_keyboard(user_words)
            await query.edit_message_text(text=answer, reply_markup=reply_markup)
            return THREE

    async def settings_services(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        print(context.user_data["user"])
        query = update.callback_query
        await query.answer()
        answer = query.data
        print(answer)
        await query.edit_message_text(text=answer)
        return ConversationHandler.END

    async def settings_words(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        print(context.user_data["user"])
        query = update.callback_query
        await query.answer()
        answer = query.data
        print(answer)
        await query.edit_message_text(text=answer)
        return ConversationHandler.END

    async def command_techsupport(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        try:
            self.db.get_user(self.db_conn, update.effective_user.id)
            msg = "<b>Задайте вопрос:</b>\nДля отмены - /cancel"
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
            return ONE
        except IndexError:
            await update.message.reply_text(self.auth_invalid_msg)

    async def techsupport_msg(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """TODO: save techsupport ticket - update.message.text"""
        msg = "<b>Вопрос отправлен!</b>В ближайшее время, вы получите ответ."
        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    async def command_help(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        try:
            self.db.get_user(self.db_conn, update.effective_user.id)
            msg = "\n".join(
                [
                    "<b>Доступные команды:</b>",
                    f"{self.commands['start']} - Регистрация",
                    f"{self.commands['help']} - Помошник команд",
                    f"{self.commands['pay']} - Пополнить баланс",
                    f"{self.commands['bill']} - Текущий тарифный план",
                    f"{self.commands['settings']} - Настройки оповещения",
                    f"{self.commands['techsupport']} - Техническая поддержка",
                    f"{self.commands['cancel']} - Прервать диалог",
                ]
            )
            await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
        except IndexError:
            await update.message.reply_text(self.auth_invalid_msg)

    async def command_cancel_conv(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """Cancels and ends the conversation."""
        msg = "Операция прервана"
        await update.message.reply_text(msg, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

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
            chat_id=self.env["TELEGRAM_ADMIN_ID"],
            text=message,
            parse_mode=ParseMode.HTML,
        )

    def run(self):
        """Run telegram bot instance"""
        # Create the Application and pass it your bot's token.
        application = Application.builder().token(self.api_token).build()
        # conversations
        start_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.command_start)],
            states={
                ONE: [CallbackQueryHandler(self.auth_service)],
                TWO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.auth_words)],
                THREE: [CallbackQueryHandler(self.auth_words_confirm)],
            },
            fallbacks=[CommandHandler("cancel", self.command_cancel_conv)],
            per_user=True,
        )
        pay_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("pay", self.command_pay)],
            states={
                ONE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.build_invoice)
                ]
            },
            fallbacks=[CommandHandler("cancel", self.command_cancel_conv)],
            per_user=True,
        )
        settings_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("settings", self.command_settings)],
            states={
                ONE: [CallbackQueryHandler(self.settings_choose)],
                TWO: [CallbackQueryHandler(self.settings_services)],
                THREE: [CallbackQueryHandler(self.settings_words)],
            },
            fallbacks=[CommandHandler("cancel", self.command_cancel_conv)],
            per_user=True,
        )
        techsupport_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("techsupport", self.command_techsupport)],
            states={
                ONE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.techsupport_msg
                    )
                ]
            },
            fallbacks=[CommandHandler("cancel", self.command_cancel_conv)],
            per_user=True,
        )
        # generic handlers
        application.add_handler(start_conv_handler)
        application.add_handler(settings_conv_handler)
        application.add_handler(techsupport_conv_handler)
        application.add_handler(CommandHandler("balance", self.command_balance))
        application.add_handler(CommandHandler("bill", self.command_bill))
        application.add_handler(CommandHandler("help", self.command_help))
        # payments
        application.add_handler(pay_conv_handler)
        application.add_handler(PreCheckoutQueryHandler(self.precheckout_callback))
        application.add_handler(
            MessageHandler(filters.SUCCESSFUL_PAYMENT, self.successful_payment_callback)
        )
        #  error handler
        application.add_error_handler(self.error_handler)
        # Run the bot until the user presses Ctrl-C
        application.run_polling()


if __name__ == "__main__":
    import environ

    env = environ.Env()
    api_token = env.bool("TELEGRAM_API_TOKEN", False)
    telegram_bot = TelegramBot(api_token=api_token)
    telegram_bot.run()
