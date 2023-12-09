from logging import Logger
from telegram.ext import Updater
from utils import Config
from dotenv import load_dotenv
from container import Container


def main() -> None:
    load_dotenv()
    config: Config = Config()
    container: Container = Container()
    updater: Updater = container.updater()
    dispatcher = updater.dispatcher

    logger: Logger = container.logger()
    logger.info("Starting the bot's polling...")
    updater.start_polling()

    logger.info("Bot is now in idle state.")
    updater.idle()


if __name__ == "__main__":
    main()
