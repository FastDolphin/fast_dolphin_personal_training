import os
from typing import Dict, Any, Union, List
import requests
from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)
from typeguard import typechecked
from utils import Config, Prompts
from requests import Response
from logging import Logger
from ..send_menu import send_menu_handler_factory

TOKEN = 0


@typechecked
def authorize_handler_factory(cfg: Config, logger: Logger, messages: Dict[str, Any]):
    @typechecked
    def get_token(update: Update, context: CallbackContext) -> int:
        if update.effective_chat is None:
            raise ValueError
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Пожалуйста, введите ваш токен:",
        )
        return TOKEN

    @typechecked
    def receive_and_set_api_key_token(
        update: Update, context: CallbackContext
    ) -> Union[int, None]:
        if update.effective_chat is None:
            raise TypeError
        context.user_data["api_token"] = update.message.text
        user_chat_id = str(update.effective_chat.id)

        params = {
            "api_key": context.user_data["api_token"],
        }

        logger.info(
            f"User: {user_chat_id} insered a token: {context.user_data['api_token']}\n"
        )

        try:
            get_response: Response = requests.get(
                f"{cfg.BACKEND_API}/{cfg.VERSION}/{cfg.ALLOWED_PERSONAL_TRAINING}",
                params=params,
                timeout=10,
            )

            logger.debug(
                f"Received HTTP {get_response.status_code} from backend for allowance request."
            )

            if get_response.status_code == 403:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="ОЙ! Доступа нет! :(",
                )
                send_menu_handler = send_menu_handler_factory(cfg)
                send_menu_handler(update, context)
                return ConversationHandler.END
            else:
                get_response.raise_for_status()

            data = get_response.json()

            if isinstance(data, dict):
                resources: List[Dict[str, Any]] = data["Resources"]
                if not resources:  # If list is empty
                    logger.warning(
                        f"No current training plans found for user {user_chat_id}."
                    )
                    context.bot.send_message(
                        chat_id=update.effective_chat.id, text="Такого токена нет :("
                    )
                else:
                    for resource in resources:
                        if isinstance(resource, dict):
                            is_allowed: bool = resource["Allowed"]
                            if is_allowed:
                                os.environ["X-API-Key"] = context.user_data["api_token"]
                                context.bot.send_message(
                                    chat_id=update.effective_chat.id,
                                    text="Отлично! Солнышко, я тебя узнал! Ты моя умничка, давай начнем тренировки!!!",
                                )
                                send_menu_handler = send_menu_handler_factory(cfg)
                                send_menu_handler(update, context)
                                return ConversationHandler.END
                            else:
                                context.bot.send_message(
                                    chat_id=update.effective_chat.id,
                                    text="Ой! А доступ уже закончился! Нужно запросить новый!",
                                )
                                send_menu_handler = send_menu_handler_factory(cfg)
                                send_menu_handler(update, context)
                                return ConversationHandler.END

        except requests.Timeout:
            logger.warning(
                f"Request to backend for training plan timed out for user {user_chat_id}."
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=messages["request_timeout"]
            )
        except (
            requests.RequestException
        ) as e:  # Catching other request-related exceptions
            logger.error(f"Request to backend failed with error: {str(e)}")
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=messages["exception"].format(exception=str(e)),
            )
        except ValueError:  # This will catch non-JSON parsable responses
            logger.error(
                f"Received non-JSON parsable response from backend for user {user_chat_id}."
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=messages["unexpected_data"]
            )

    return get_token, receive_and_set_api_key_token


@typechecked
def get_authorize_handler(
    cfg: Config, logger: Logger, messages: Dict[str, Any]
) -> ConversationHandler:
    get_token, receive_and_set_api_key_token = authorize_handler_factory(
        cfg, logger, messages
    )

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(get_token, pattern="get_token")],
        states={
            TOKEN: [
                MessageHandler(
                    Filters.text & ~Filters.command, receive_and_set_api_key_token
                )
            ]
        },
        fallbacks=[],
    )
    return conv_handler
