from typing import Callable
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
)
from utils import Config, Commands
from typeguard import typechecked


@typechecked
def send_menu_handler_factory(
    cfg: Config, commands: Commands
) -> Callable[[Update, CallbackContext], None]:
    @typechecked
    def send_menu(update: Update, context: CallbackContext) -> None:
        if update.effective_chat is None:
            raise TypeError

        user_chat_id = str(update.effective_chat.id)

        commands_text: str
        if user_chat_id == cfg.ADMIN_CHAT_ID:
            commands_text = "\n".join(
                [f"{cmd} - {desc}" for cmd, desc in commands.ADMIN.items()]
            )
        elif user_chat_id == cfg.CLIENT_CHAT_ID:
            commands_text = "\n".join(
                [f"{cmd} - {desc}" for cmd, desc in commands.CLIENT.items()]
            )

        else:
            commands_text = "\n".join(
                [f"{cmd} - {desc}" for cmd, desc in commands.USER.items()]
            )
        context.bot.send_message(chat_id=update.effective_chat.id, text=commands_text)
    return send_menu


@typechecked
def get_send_menu_handler(cfg: Config, commands: Commands) -> CommandHandler:
    send_menu_handler = send_menu_handler_factory(cfg, commands)
    return CommandHandler("menu", send_menu_handler)
