import json
from typing import Dict, Any, Union

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
from utils import Config, format_report_with_gpt, ReportWithMetadata, Prompts
from requests import Response
from logging import Logger
from ..send_menu import send_menu_handler_factory

CLIENT_REPORT = 0


@typechecked
def send_report_handler_factory(
    cfg: Config, prompts: Prompts, logger: Logger, messages: Dict[str, Any]
):
    def send_report(update: Update, context: CallbackContext) -> int:
        if update.effective_chat is None:
            raise ValueError
        user_chat_id = str(update.effective_chat.id)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Пожалуйста, напишите свой отчет о тренировке:",
        )
        return CLIENT_REPORT

    def receive_and_load_report(
        update: Update, context: CallbackContext
    ) -> Union[int, None]:
        if update.effective_chat is None:
            raise TypeError
        user_chat_id = str(update.effective_chat.id)

        current_year: int = 2023
        current_week: int = 50

        # get user's input (string)
        client_response: Union[str, None] = update.message.text
        if update.message.text is None:
            raise ValueError
        elif isinstance(client_response, str):
            client_report: str = client_response

        report: ReportWithMetadata = format_report_with_gpt(
            cfg=cfg,
            prompts=prompts,
            tg_id=int(user_chat_id),
            year=current_year,
            week=current_week,
            client_report=client_report,
        )

        logger.debug(f"Report: {json.dumps(report.dict())}")

        try:
            # # Send request to backend
            # response: Response = requests.post(
            #     f"{cfg.BACKEND_API}/{cfg.VERSION}/{cfg.CLIENT_REPORT_ENDPOINT}",
            #     timeout=10,
            #     json=report.dict(),
            # )
            #
            # logger.debug(
            #     f"Received HTTP {response.status_code} from backend for training plan request."
            # )
            #
            # # Raise exception for HTTP errors
            # response.raise_for_status()

            # response_dict: Dict[str, Any] = response.json()
            # get year and week from response_dict
            year = 2023
            week = 50

            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=messages["report_successfully_uploaded"].format(
                    year=year, week=week
                ),
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

        send_menu_handler = send_menu_handler_factory(cfg)
        send_menu_handler(update, context)
        return None

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