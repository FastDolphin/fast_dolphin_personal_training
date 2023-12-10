from logging import Logger
from typing import Callable, Dict, Any

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
)

from utils import Config, Commands
from typeguard import typechecked
from ..get_personal_training import send_personal_training_handler_factory
from ..get_description import get_description_handler_factory
from ..send_report import send_report_handler_factory


@typechecked
def callback_query_handler_factory(
    cfg: Config, commands: Commands, logger: Logger, messages: Dict[str, Any]
) -> Callable[[Update, CallbackContext], None]:
    @typechecked
    def callback_query(update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        query.answer()

        user_chat_id = str(update.effective_chat.id)

        if query.data == "get_description" and user_chat_id in [
            cfg.ADMIN_CHAT_ID,
            cfg.CLIENT_CHAT_ID,
        ]:
            get_description_handler = get_description_handler_factory(cfg, messages)
            get_description_handler(update, context)

        elif query.data == "get_personal_training" and user_chat_id in [
            cfg.ADMIN_CHAT_ID,
            cfg.CLIENT_CHAT_ID,
        ]:
            personal_training_handler = send_personal_training_handler_factory(
                cfg, logger, messages
            )
            personal_training_handler(update, context)

        elif query.data == "send_report" and user_chat_id in [
            cfg.ADMIN_CHAT_ID,
            cfg.CLIENT_CHAT_ID,
        ]:
            send_report_handler = send_report_handler_factory(cfg)
            send_report_handler(update, context)

        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text="Доступ запрещен."
            )

    return callback_query


@typechecked
def get_callback_query_handler(
    cfg: Config, commands: Commands, logger: Logger, messages: Dict[str, Any]
) -> CallbackQueryHandler:
    callback_query_handler = callback_query_handler_factory(
        cfg, commands, logger, messages
    )
    return CallbackQueryHandler(callback_query_handler)
