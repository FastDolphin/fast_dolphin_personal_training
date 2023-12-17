from logging import Logger
from typing import Callable, Dict, Any

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
)

from utils import Config, Commands, Prompts
from typeguard import typechecked
from ..get_personal_training import send_personal_training_handler_factory
from ..get_description import get_description_handler_factory
from ..send_report import send_report_handler_factory


@typechecked
def callback_query_handler_factory(
    cfg: Config, logger: Logger, messages: Dict[str, Any]
) -> Callable[[Update, CallbackContext], None]:
    @typechecked
    def callback_query(update: Update, context: CallbackContext) -> None:
        query = update.callback_query
        query.answer()
        if update.effective_chat is None:
            raise TypeError

        if query.data == "get_description":
            get_description_handler = get_description_handler_factory(cfg, messages)
            get_description_handler(update, context)

        elif query.data == "get_personal_training":
            personal_training_handler = send_personal_training_handler_factory(
                cfg, logger, messages
            )
            personal_training_handler(update, context)

    return callback_query


@typechecked
def get_callback_query_handler(
    cfg: Config, logger: Logger, messages: Dict[str, Any]
) -> CallbackQueryHandler:
    callback_query_handler = callback_query_handler_factory(cfg, logger, messages)
    return CallbackQueryHandler(callback_query_handler)
