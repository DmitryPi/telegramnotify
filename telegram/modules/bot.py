import asyncio  # noqa isort:skip
import html
import json
import logging
import traceback

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

from .utils import load_config


class SenderBot:
    pass


class TelegramBot:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.config = load_config()

    @property
    def auth_invalid_msg(self) -> str:
        return "Пройдите идентификацию.\nИспользуйте команду - /start"

    async def command_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        print(user_id)
        await update.message.reply_text("starting")

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
        # generic handlers
        application.add_handler(CommandHandler("start", self.command_start))
        # ...and the error handler
        application.add_error_handler(self.error_handler)
        # Run the bot until the user presses Ctrl-C
        application.run_polling()
