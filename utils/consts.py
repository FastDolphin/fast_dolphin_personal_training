import os
from typing import Literal, Pattern, AnyStr

from dotenv import load_dotenv
import re
from pydantic import BaseModel, validator

load_dotenv()


class Config(BaseModel):
    TOKEN: str = os.environ["LIUBA_TELEGRAM_TOKEN"]
    ADMIN_NAME: str = os.environ["ADMIN_NAME"]
    ADMIN_CHAT_ID: str = os.environ["ADMIN_CHAT_ID"]
    CLIENT_CHAT_ID: str = os.environ["CLIENT_CHAT_ID"]
    BACKEND_API: str = os.environ["BACKEND_API"]
    VERSION: str = "v1"
    PERSONAL_TRAINING_ENDPOINT: str = os.environ["PERSONAL_TRAINING_ENDPOINT"]
    CURRENT_PERSONAL_TRAINING_ENDPOINT: str = os.environ[
        "CURRENT_PERSONAL_TRAINING_ENDPOINT"
    ]
    PERSONAL_TRAINING_REPORT: str = os.environ["PERSONAL_TRAINING_REPORT"]
    ALLOWED_PERSONAL_TRAINING: str = os.environ["ALLOWED_PERSONAL_TRAINING"]
    MAX_MESSAGE_LENGTH: int = 4090
    MESSAGES_DIR: Literal["messages"] = "messages"
    MESSAGES_FILE: Literal["messages.json"] = "messages.json"
    OPENAI_API_KEY: str = os.environ["OPENAI_API_KEY"]

    LOG_DIR: str = "logs"
    LOG_FILE_NAME: str = "logs.log"
    OUTPUT_LOG_FILE_NAME: str = "logs.txt"

    OPENAI_API_URL: str = "https://api.openai.com/v1/chat/completions"
    MODEL_TYPE: str = "gpt-4"

    @validator("TOKEN", pre=True, always=True)
    def validate_and_process_token(cls, value):
        if not re.match(r"^\d+:[A-Za-z0-9_-]+$", value):
            raise ValueError("Invalid Telegram bot token format")
        return value

    @validator("ADMIN_CHAT_ID", pre=True, always=True)
    def validate_and_process_tg_chat_id(cls, value):
        if not re.match(r"^-?\d+$", value):
            raise ValueError("Invalid Admin chat_id format")
        return value


EMAIL_PATTERN: Pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
PHONE_PATTERN: Pattern = re.compile(
    r"^(?:\+7|8)[- ]?(?:\d{3}[- ]?\d{3}[- ]?\d{2}[- ]?\d{2})$"
)
