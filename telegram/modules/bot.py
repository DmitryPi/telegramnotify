import asyncio  # noqa isort:skip
import html
import json
import logging
import traceback

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler

from .db import Database
from .utils import load_config

ONE, TWO, THREE = (i for i in range(1, 4))


class SenderBot:
    pass


class TelegramBot:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.config = load_config()
        self.db = Database()
        self.db_conn = self.db.create_connection()
        self.services = ["FL.ru", "avito"]

    @property
    def auth_invalid_msg(self) -> str:
        return "Пройдите регистрацию.\nИспользуйте команду - /start"

    def build_keyboard_markup(self, context: list[str], grid=3) -> InlineKeyboardMarkup:
        """TODO: btn grid division"""
        btns = [InlineKeyboardButton(s, callback_data=s) for s in context]
        reply_markup = InlineKeyboardMarkup([btns])
        return reply_markup

    async def command_start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        try:
            self.db.get_user(self.db_conn, update.effective_user.id)
            msg = "\n".join(
                [
                    "Постоянное приветствие",
                ]
            )
            await update.message.reply_text("")
        except IndexError:
            msg = "\n".join(
                [
                    "Привет, я тебя еще не видел!",
                    "Я могу оповещать тебя о новых работах и проектах",
                    "\nВыбери сервис:",
                ]
            )
            reply_markup = self.build_keyboard_markup(self.services)
            await update.message.reply_text(msg, reply_markup=reply_markup)
            return ONE

    async def command_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            self.db.get_user(self.db_conn, update.effective_user.id)
            msg = "\n".join(
                [
                    "<b>Доступные команды:</b>",
                    "/start - Регистрация",
                    "/help - Помошник команд",
                    "/cancel - Прервать диалог",
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
            chat_id=self.config["TELEGRAM"]["admin_id"],
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
                ONE: [],
            },
            fallbacks=[CommandHandler("cancel", self.command_cancel_conv)],
            per_user=True,
        )
        # generic handlers
        application.add_handler(start_conv_handler)
        application.add_handler(CommandHandler("help", self.command_help))
        # ...and the error handler
        application.add_error_handler(self.error_handler)
        # Run the bot until the user presses Ctrl-C
        application.run_polling()
