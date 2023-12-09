import json
import os
from typing import Dict, Any
from typeguard import typechecked
from logging import Logger
from .consts import Config
from datetime import date


@typechecked
def load_messages(message_path: str, logger: Logger) -> Dict[str, Any]:
    if not os.path.exists(message_path):
        raise FileNotFoundError("Messages are not found")

    try:
        with open(message_path, "r", encoding="utf-8") as file:
            messages: Dict[str, Any] = json.load(file)
            logger.info(f"Successfully loaded messages from {message_path}")
        return messages
    except Exception as e:
        logger.error(f"Failed to load messages from {message_path} due to error: {e}")
        return {}


@typechecked
def convert_json_personal_training_to_human_readable(data: Dict[str, Any]) -> str:
    return ""


@typechecked
def is_admin(cfg: Config, user_chat_id: str) -> bool:
    return user_chat_id == cfg.ADMIN_CHAT_ID


@typechecked
def is_client(cfg: Config, user_chat_id: str) -> bool:
    return user_chat_id in cfg.CLIENT_CHAT_ID


@typechecked
def fetch_calender_week() -> int:
    return date.today().isocalendar()[1]
