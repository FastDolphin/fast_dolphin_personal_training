import os
import json
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
from utils import Config, format_report_with_gpt, ReportWithMetadata, Prompts, MetaData
from requests import Response
from logging import Logger
from ..send_menu import send_menu_handler_factory

CLIENT_REPORT = 0


@typechecked
def send_report_handler_factory(
    cfg: Config, prompts: Prompts, logger: Logger, messages: Dict[str, Any]
):
    @typechecked
    def send_report(update: Update, context: CallbackContext) -> int:
        if update.effective_chat is None:
            raise ValueError
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=messages["please_write_report"],
        )
        return CLIENT_REPORT

    @typechecked
    def receive_and_load_report(
        update: Update, context: CallbackContext
    ) -> Union[int, None]:
        if update.effective_chat is None:
            raise TypeError
        user_chat_id = str(update.effective_chat.id)

        params = {
            "tg_id": user_chat_id,
        }
        headers: Dict[str, str] = {
            "accept": "application/json",
            "X-API-Key": os.environ["X-API-Key"],
        }

        logger.info(f"User: {user_chat_id} requested current training plan idx\n")

        try:
            # Send request to backend
            get_response: Response = requests.get(
                f"{cfg.BACKEND_API}/{cfg.VERSION}/{cfg.CURRENT_PERSONAL_TRAINING_ENDPOINT}",
                headers=headers,
                params=params,
                timeout=10,
            )

            logger.debug(
                f"Received HTTP {get_response.status_code} from backend for metadata request."
            )

            if get_response.status_code == 404:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=messages["first_train_then_report"],
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
                    formatted_data = messages["no_current_personal_training"]
                    logger.warning(
                        f"No current training plans found for user {user_chat_id}."
                    )
                    context.bot.send_message(
                        chat_id=update.effective_chat.id, text=formatted_data
                    )
                else:
                    for resource in resources:
                        if isinstance(resource, dict):
                            metadata: MetaData = MetaData(**resource)
                            client_response: Union[str, None] = update.message.text
                            client_report: str = ""
                            if update.message.text is None:
                                raise ValueError
                            elif isinstance(client_response, str):
                                client_report: str = client_response

                            report: ReportWithMetadata = format_report_with_gpt(
                                cfg=cfg,
                                prompts=prompts,
                                metadata=metadata,
                                client_report=client_report,
                            )

                            post_response: Response = requests.post(
                                f"{cfg.BACKEND_API}/{cfg.VERSION}/{cfg.PERSONAL_TRAINING_REPORT}",
                                headers=headers,
                                timeout=10,
                                json=report.dict(),
                            )
                            logger.debug(
                                f"Received HTTP {post_response.status_code} from backend for post report request."
                            )
                            if post_response.status_code == 409:
                                context.bot.send_message(
                                    chat_id=update.effective_chat.id,
                                    text=messages["report_already_exists"].format(
                                        week=metadata.Week, year=metadata.Year
                                    ),
                                )
                                send_menu_handler = send_menu_handler_factory(cfg)
                                send_menu_handler(update, context)
                                return ConversationHandler.END
                            else:
                                post_response.raise_for_status()

                            logger.debug(f"Report: {json.dumps(report.dict())}")
                            try:
                                context.bot.send_message(
                                    chat_id=update.effective_chat.id,
                                    text=messages[
                                        "report_successfully_uploaded"
                                    ].format(year=metadata.Year, week=metadata.Week),
                                )

                                send_menu_handler = send_menu_handler_factory(cfg)
                                send_menu_handler(update, context)
                                return ConversationHandler.END

                            except requests.Timeout:
                                logger.warning(
                                    f"Request to backend for training plan timed out for user {user_chat_id}."
                                )
                                context.bot.send_message(
                                    chat_id=update.effective_chat.id,
                                    text=messages["request_timeout"],
                                )
                            except (
                                requests.RequestException
                            ) as e:  # Catching other request-related exceptions
                                logger.error(
                                    f"Request to backend failed with error: {str(e)}"
                                )
                                context.bot.send_message(
                                    chat_id=update.effective_chat.id,
                                    text=messages["exception"].format(exception=str(e)),
                                )
                            except (
                                ValueError
                            ):  # This will catch non-JSON parsable responses
                                logger.error(
                                    f"Received non-JSON parsable response from backend for user {user_chat_id}."
                                )
                                context.bot.send_message(
                                    chat_id=update.effective_chat.id,
                                    text=messages["unexpected_data"],
                                )

                            send_menu_handler = send_menu_handler_factory(cfg)
                            send_menu_handler(update, context)
                            return None
                        else:
                            raise TypeError

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

    return send_report, receive_and_load_report


@typechecked
def get_send_report_handler(
    cfg: Config, prompts: Prompts, logger: Logger, messages: Dict[str, Any]
) -> ConversationHandler:
    send_report, receive_and_load_report = send_report_handler_factory(
        cfg, prompts, logger, messages
    )

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(send_report, pattern="send_report")],
        states={
            CLIENT_REPORT: [
                MessageHandler(Filters.text & ~Filters.command, receive_and_load_report)
            ]
        },
        fallbacks=[],
    )
    return conv_handler
