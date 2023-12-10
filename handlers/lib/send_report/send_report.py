from telegram import Update
from telegram.ext import CallbackContext

from utils import Config


def send_report_handler_factory(cfg: Config):
    def send_report(update: Update, context: CallbackContext) -> None:
        if update.effective_chat is None:
            raise TypeError

        user_chat_id = str(update.effective_chat.id)

        raise NotImplementedError

    return send_report
