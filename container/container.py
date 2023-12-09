from dependency_injector import containers, providers
from telegram.ext import Updater
from logger import init_logger

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    updater = providers.Singleton(
        Updater, token=config.telegram.token, use_context=True
    )
    logger = providers.Singleton(
        init_logger, use_context=True
    )
