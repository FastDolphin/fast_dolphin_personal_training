from typing import Dict, Any, List, Callable
from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    Filters,
)
import requests
from utils import (
    Config,
    convert_json_personal_training_to_human_readable,
    is_client,
    is_admin,
    fetch_calender_week,
)
from ..cancel import cancel
from logging import Logger
from typeguard import typechecked

(
    GROUP_LEVEL,
    CALENDER_WEEK,
    TRAINING_DAY,
) = range(3)


@typechecked
def get_personal_training_handler_factory(
    cfg: Config, logger: Logger, messages: Dict[str, Any]
) -> Callable[[Update, CallbackContext], int]:
    @typechecked
    def get_personal_training(
        update: Update,
        context: CallbackContext,
    ):
        if update.effective_chat is None:
            raise TypeError
        user_chat_id = str(update.effective_chat.id)
        username = (
            update.effective_user.username or "unknown"
        )  # Use the username if available, else 'unknown'

        logger.info(
            f"Incoming request for training plan from user: {username} (ID: {user_chat_id})."
        )

        if is_admin(user_chat_id) or is_client(user_chat_id):
            # Step 1: Ask for the parameters
            logger.debug(
                f"User: {username} (ID: {user_chat_id}) is identified as admin/coach. Requesting group level details."
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=messages["enter_group_level"]
            )
            return GROUP_LEVEL

        else:
            logger.warning(
                f"User: {username} (ID: {user_chat_id}) tried to access training plan without necessary permissions."
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=messages["not_allowed"]
            )
            return ConversationHandler.END

    return get_personal_training


@typechecked
def get_get_personal_training_handler(
    cfg: Config, logger: Logger, messages: Dict[str, Any]
) -> CommandHandler:
    get_personal_training_handler = get_personal_training_handler_factory(
        cfg, logger, messages
    )
    return CommandHandler("get_personal_training", get_personal_training_handler)


#
# @typechecked
# def ask_for_week(update: Update, context: CallbackContext, messages: Dict[str, Any]):
#     context.user_data["level"] = update.message.text
#     context.bot.send_message(
#         chat_id=update.effective_chat.id, text=messages["enter_current_calender_week"]
#     )
#     return CALENDER_WEEK
#
#
# @typechecked
# def ask_for_day(update: Update, context: CallbackContext, messages: Dict[str, Any]):
#     context.user_data["week"] = update.message.text
#     context.bot.send_message(
#         chat_id=update.effective_chat.id, text=messages["enter_current_training_day"]
#     )
#     return TRAINING_DAY
#
#
# @typechecked
# def send_training_plan(
#     update: Update,
#     context: CallbackContext,
#     cfg: Config,
#     logger: Logger,
#     messages: Dict[str, Any],
# ) -> int:
#     if update.effective_chat is None:
#         raise TypeError
#
#     user_chat_id = str(update.effective_chat.id)
#
#     context.user_data["day"] = update.message.text
#     params = {
#         "level": context.user_data["level"],
#         "week": context.user_data["week"],
#         "day": context.user_data["day"],
#     }
#
#     logger.info(
#         f"User: {user_chat_id} requested training plan for\n"
#         f"Level: {context.user_data['level']},\n"
#         f"Week: {context.user_data['week']},\n"
#         f"Day: {context.user_data['day']}"
#     )
#
#     try:
#         # Send request to backend
#         response = requests.get(
#             f"{cfg.BACKEND_API}/{cfg.VERSION}/{cfg.PERSONAL_TRAINING_ENDPOINT}",
#             params=params,
#             timeout=10,
#         )
#
#         logger.debug(
#             f"Received HTTP {response.status_code} from backend for training plan request."
#         )
#
#         # Raise exception for HTTP errors
#         response.raise_for_status()
#
#         # Try parsing the JSON response
#         data = response.json()
#
#         # Check the type of the data received
#         if isinstance(data, dict):
#             resource: Dict[str, Any] = data["Resources"][0]
#             formatted_data = convert_json_personal_training_to_human_readable(resource)
#
#         else:
#             formatted_data = str(data)
#
#         # Split the formatted_data into chunks to be sent in multiple messages if needed
#         data_chunks = [
#             formatted_data[i : i + cfg.MAX_MESSAGE_LENGTH]
#             for i in range(0, len(formatted_data), cfg.MAX_MESSAGE_LENGTH)
#         ]
#
#         for chunk in data_chunks:
#             context.bot.send_message(chat_id=update.effective_chat.id, text=chunk)
#             logger.debug(f"Sent message chunk to user {user_chat_id}.")
#
#     except requests.Timeout:
#         logger.warning(
#             f"Request to backend for training plan timed out for user {user_chat_id}."
#         )
#         context.bot.send_message(
#             chat_id=update.effective_chat.id, text=messages["request_timeout"]
#         )
#     except requests.RequestException as e:  # Catching other request-related exceptions
#         logger.error(f"Request to backend failed with error: {str(e)}")
#         context.bot.send_message(
#             chat_id=update.effective_chat.id,
#             text=messages["no_training_plan"],
#         )
#     except ValueError:  # This will catch non-JSON parsable responses
#         logger.error(
#             f"Received non-JSON parsable response from backend for user {user_chat_id}."
#         )
#         context.bot.send_message(
#             chat_id=update.effective_chat.id, text=messages["unexpected_data"]
#         )
#     logger.info(f"Sending menu to user {user_chat_id}.")
#     return ConversationHandler.END


@typechecked
def send_personal_training_handler_factory(
    cfg: Config, logger: Logger, messages: Dict[str, Any]
) -> Callable[[Update, CallbackContext], int]:
    @typechecked
    def send_personal_training_for_current_week(
        update: Update,
        context: CallbackContext,
    ) -> int:
        if update.effective_chat is None:
            raise TypeError

        user_chat_id = str(update.effective_chat.id)

        context.user_data["level"] = update.message.text
        params = {
            "level": context.user_data["level"],
            "week": fetch_calender_week(),
        }

        logger.info(
            f"User {user_chat_id} requested training plan for\n"
            f"Level: {context.user_data['level']},\n"
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
                    formatted_data = messages["no_training_plan"]
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
                text=messages["no_training_plan"],
            )
        except ValueError:  # This will catch non-JSON parsable responses
            logger.error(
                f"Received non-JSON parsable response from backend for user {user_chat_id}."
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=messages["unexpected_data"]
            )
        logger.info(f"Sending menu to user {user_chat_id}.")
        return ConversationHandler.END

    return send_personal_training_for_current_week


# conv_handler_training_plan = ConversationHandler(
#     entry_points=[CommandHandler("get_personal_training", get_personal_training)],
#     states={
#         GROUP_LEVEL: [MessageHandler(Filters.text & ~Filters.command, ask_for_week)],
#         CALENDER_WEEK: [MessageHandler(Filters.text & ~Filters.command, ask_for_day)],
#         TRAINING_DAY: [
#             MessageHandler(Filters.text & ~Filters.command, send_training_plan)
#         ],
#     },
#     fallbacks=[CommandHandler("cancel", cancel)],
# )


# conv_handler_training_plan_for_current_week = ConversationHandler(
#     entry_points=[
#         CommandHandler("get_personal_training_current_week", get_personal_training)
#     ],
#     states={
#         GROUP_LEVEL: [
#             MessageHandler(
#                 Filters.text & ~Filters.command, send_personal_training_for_current_week
#             )
#         ],
#     },
#     fallbacks=[CommandHandler("cancel", cancel)],
# )


@typechecked
def get_training_plan_conversation_handler(
    cfg: Config, logger: Logger, messages: Dict[str, Any]
) -> ConversationHandler:
    send_personal_training_handler = send_personal_training_handler_factory(
        cfg, logger, messages
    )
    get_personal_training_handler = get_get_personal_training_handler(
        cfg, logger, messages
    )

    return ConversationHandler(
        entry_points=[get_personal_training_handler],
        states={
            GROUP_LEVEL: [
                MessageHandler(
                    Filters.text & ~Filters.command, send_personal_training_handler
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
