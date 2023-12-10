from typing import Dict, Any, List, Callable
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
)
import requests
from utils import (
    Config,
    convert_json_personal_training_to_human_readable,
    fetch_calender_week,
)
from logging import Logger
from typeguard import typechecked
from ..send_menu import send_menu_handler_factory


@typechecked
def send_personal_training_handler_factory(
    cfg: Config, logger: Logger, messages: Dict[str, Any]
) -> Callable[[Update, CallbackContext], None]:
    @typechecked
    def send_personal_training_for_current_week(
        update: Update,
        context: CallbackContext,
    ) -> None:
        if update.effective_chat is None:
            raise TypeError

        user_chat_id = str(update.effective_chat.id)
        current_calender_week: int = fetch_calender_week()
        params = {
            "tg_id": user_chat_id,
            "year": 2023,
            "week": current_calender_week,
        }

        logger.info(
            f"TgId: {user_chat_id}\n"
            f"User: {user_chat_id} requested training plan for\n"
            f"Week: {params['week']}"
        )

        try:
            # Send request to backend
            response = requests.get(
                f"{cfg.BACKEND_API}/{cfg.VERSION}/{cfg.PERSONAL_TRAINING_ENDPOINT}",
                params=params,
                timeout=10,
            )

            logger.debug(
                f"Received HTTP {response.status_code} from backend for training plan request."
            )

            # Raise exception for HTTP errors
            response.raise_for_status()

            # Try parsing the JSON response
            data = response.json()

            if isinstance(data, dict):
                resources: List[Dict[str, Any]] = data["Resources"]
                if not resources:  # If list is empty
                    formatted_data = messages["no_personal_training"].format(
                        calendar_week=current_calender_week
                    )
                    logger.warning(
                        f"No training plans found for user {user_chat_id} for given criteria."
                    )
                else:
                    formatted_list = []
                    for resource in resources:
                        if isinstance(resource, dict):
                            formatted_resource = (
                                convert_json_personal_training_to_human_readable(
                                    resource
                                )
                            )
                            formatted_list.append(formatted_resource)
                        else:
                            formatted_list.append(str(resource))
                    formatted_data = "\n".join(formatted_list)
            else:
                formatted_data = str(data)

            # Split the formatted_data into chunks to be sent in multiple messages if needed
            data_chunks = [
                formatted_data[i : i + cfg.MAX_MESSAGE_LENGTH]
                for i in range(0, len(formatted_data), cfg.MAX_MESSAGE_LENGTH)
            ]

            for chunk in data_chunks:
                context.bot.send_message(chat_id=update.effective_chat.id, text=chunk)
                logger.debug(f"Sent message chunk to user {user_chat_id}.")
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
                text=messages["no_personal_training"].format(
                    calender_week=current_calender_week
                ),
            )
        except ValueError:  # This will catch non-JSON parsable responses
            logger.error(
                f"Received non-JSON parsable response from backend for user {user_chat_id}."
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=messages["unexpected_data"]
            )

        send_menu_handler = send_menu_handler_factory(cfg)
        send_menu_handler(update, context)

    return send_personal_training_for_current_week


@typechecked
def get_training_plan_conversation_handler(
    cfg: Config, logger: Logger, messages: Dict[str, Any]
) -> CommandHandler:
    get_personal_training_handler = send_personal_training_handler_factory(
        cfg, logger, messages
    )
    return CommandHandler("get_personal_training", get_personal_training_handler)
