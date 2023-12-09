from logging import Logger
from typing import Dict, Any

from telegram.ext import Updater
from utils import Config, Commands
from dotenv import load_dotenv
from container import Container
from handlers import get_start_handler, get_send_menu_handler


def main() -> None:
    load_dotenv()
    container: Container = Container()
    cfg: Config = container.config()
    commands: Commands = container.commands()
    messages: Dict[str, Any] = container.messages()

    updater: Updater = container.updater()
    dispatcher = updater.dispatcher

    start_handler = get_start_handler(cfg, messages)
    send_menu_command_handler = get_send_menu_handler(cfg, commands)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(send_menu_command_handler)

    logger: Logger = container.logger()
    logger.info("Starting the bot's polling...")
    updater.start_polling()

    logger.info("Bot is now in idle state.")
    updater.idle()


if __name__ == "__main__":
    main()
