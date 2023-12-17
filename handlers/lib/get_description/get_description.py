from typing import Dict, Any, Callable
from typeguard import typechecked
from telegram import Update
from telegram.ext import CallbackContext
from utils import Config


@typechecked
def get_description_handler_factory(
    cfg: Config, messages: Dict[str, Any]
) -> Callable[[Update, CallbackContext], None]:
    def get_description(update: Update, context: CallbackContext) -> None:
        if update.effective_chat is None:
            raise TypeError
        title: str = messages["description_title"]
        info = messages["description_info"]

        message_with_title: str = title + info
        data_chunks = [
            message_with_title[i : i + cfg.MAX_MESSAGE_LENGTH]
            for i in range(0, len(message_with_title), cfg.MAX_MESSAGE_LENGTH)
        ]
        for chunk in data_chunks:
            context.bot.send_message(chat_id=update.effective_chat.id, text=chunk)

    return get_description
