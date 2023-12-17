from typing import Dict, Any, Callable
from telegram import Update
from utils import Config
from typeguard import typechecked
from telegram.ext import CallbackContext, CommandHandler
from ..send_menu import send_menu_handler_factory


@typechecked
def start_handler_factory(
    messages: Dict[str, Any], cfg: Config
) -> Callable[[Update, CallbackContext], None]:
    @typechecked
    def start(update: Update, context: CallbackContext) -> None:
        if update.effective_chat is None:
            raise TypeError
        user_chat_id: str = str(update.effective_chat.id)
        greeting_message: str
        if user_chat_id == cfg.ADMIN_CHAT_ID:
            greeting_message = messages["start_message_admin"].format(
                admin_name=cfg.ADMIN_NAME
            )
        else:
            greeting_message = messages["start_message"]

        context.bot.send_message(
            chat_id=update.effective_chat.id, text=greeting_message
        )
        send_menu_handler = send_menu_handler_factory(cfg)
        send_menu_handler(update, context)

    return start


@typechecked
def get_start_handler(cfg: Config, messages: Dict[str, Any]) -> CommandHandler:
    start_handler = start_handler_factory(messages, cfg)
    return CommandHandler("start", start_handler)
