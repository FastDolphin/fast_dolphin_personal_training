from typing import Dict, Any

from dependency_injector import containers, providers
from telegram.ext import Updater
from logger import init_logger
from utils import Config, load_messages, Commands, Prompts
import os


class Container(containers.DeclarativeContainer):
    config = providers.Factory(Config)
    commands = providers.Factory(Commands)
    prompts = providers.Factory(Prompts)
    updater = providers.Singleton(Updater, token=config().TOKEN, use_context=True)
    logger = providers.Singleton(init_logger, config=config())
    message_path = os.path.join(config().MESSAGES_DIR, config().MESSAGES_FILE)

    messages: Dict[str, Any] = providers.Factory(
        load_messages, message_path=message_path, logger=logger()
    )
