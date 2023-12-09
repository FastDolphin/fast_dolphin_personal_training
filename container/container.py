from logging import Logger
from typing import Any

from dependency_injector import containers, providers
from dependency_injector.providers import Factory
from telegram.ext import Updater
from logger import init_logger
from utils import Config


class Container(containers.DeclarativeContainer):
    config: Factory[Config] = providers.Factory(Config)
    updater: Any = providers.Singleton(Updater, token=config().TOKEN, use_context=True)
    logger: Any = providers.Singleton(init_logger, config=config())
