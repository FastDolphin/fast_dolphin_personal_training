import os
from typing import Dict, Any, List, Callable
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
)
import requests
from utils import (
    Config,
    convert_json_to_human_readable,
    fetch_calender_week,
    fetch_current_year,
)
from logging import Logger
from typeguard import typechecked
from ..send_menu import send_menu_handler_factory
from requests import Response
from utils import MetaData


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
        elif isinstance(update.effective_chat.id, int):
            user_chat_id = update.effective_chat.id
        else:
            raise TypeError
        current_year: int = fetch_current_year()
        current_calender_week: int = fetch_calender_week()
        get_params: Dict[str, int] = {
            "tg_id": user_chat_id,
            "year": current_year,
            "week": current_calender_week,
        }
        headers: Dict[str, str] = {
            "accept": "application/json",
            "X-API-Key": os.environ["X-API-Key"],
        }

        logger.info(
            f"User: {get_params['tg_id']} requested training plan for\n"
            f"Week: {get_params['week']}"
        )

        try:
            # ---------------------------------------
            # ------- Get training plan ---------------
            # ---------------------------------------
            get_response: Response = requests.get(
                f"{cfg.BACKEND_API}/{cfg.VERSION}/{cfg.PERSONAL_TRAINING_ENDPOINT}",
                params=get_params,
                headers=headers,
                timeout=10,
            )
            logger.debug(
                f"Received HTTP {get_response.status_code} from backend for training plan request."
            )

            # Raise exception for HTTP errors
            get_response.raise_for_status()

            # Try parsing the JSON response
            data = get_response.json()

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
                    week_tg_ids: List[int] = [
                        resource["TgId"] for resource in resources
                    ]
                    if any(tg_id == 0 for tg_id in week_tg_ids):
                        put_params = get_params
                        put_response: Response = requests.put(
                            f"{cfg.BACKEND_API}/{cfg.VERSION}/{cfg.UPDATE_PERSONAL_TRAINING_TG_ID}",
                            params=put_params,
                            headers=headers,
                            timeout=10,
                        )
                        put_response.raise_for_status()
                        logger.info("Updated tg_id for training plan")
                    formatted_data = convert_json_to_human_readable(resources)
            else:
                formatted_data = str(data)

            # ---------------------------------------
            # ------- Update metadata ---------------
            # ---------------------------------------
            # Step 1: Delete current metadata -------

            delete_params: Dict[str, int] = {"tg_id": user_chat_id}

            delete_response: Response = requests.delete(
                f"{cfg.BACKEND_API}/{cfg.VERSION}/{cfg.CURRENT_PERSONAL_TRAINING_ENDPOINT}",
                headers=headers,
                params=delete_params,
                timeout=10,
            )

            logger.debug(
                f"Received HTTP {delete_response.status_code} from backend for delete metadata request."
            )

            if delete_response.status_code == 404:
                newcomer_welcome: str = messages["newcomer_welcome"]
                formatted_data = newcomer_welcome + formatted_data
            elif delete_response.status_code != 204:
                get_response.raise_for_status()

            # Step 2: Write current metadata --------
            metadata: MetaData = MetaData(
                TgId=user_chat_id, Year=current_year, Week=current_calender_week
            )
            post_response: Response = requests.post(
                f"{cfg.BACKEND_API}/{cfg.VERSION}/{cfg.CURRENT_PERSONAL_TRAINING_ENDPOINT}",
                headers=headers,
                timeout=10,
                json=metadata.dict(),
            )
            logger.debug(
                f"Received HTTP {post_response.status_code} from backend for post metadata request."
            )
            post_response.raise_for_status()

            # ---------------------------------------
            # ------- Respond to user ---------------
            # ---------------------------------------

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
                text=messages["exception"].format(exception=str(e)),
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
