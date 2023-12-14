from logging import Logger
from typing import Dict, Any

from telegram.ext import (
    Updater,
    CallbackQueryHandler,
    ConversationHandler,
    CommandHandler,
)
from utils import Config, Commands, Prompts
from dotenv import load_dotenv
from container import Container
from handlers import (
    get_start_handler,
    get_send_menu_handler,
    get_callback_query_handler,
    get_training_plan_conversation_handler,
    get_send_report_handler,
)


def main() -> None:
    load_dotenv()
    container: Container = Container()
    cfg: Config = container.config()
    commands: Commands = container.commands()
    prompts: Prompts = container.prompts()
    messages: Dict[str, Any] = container.messages()
    logger: Logger = container.logger()

    updater: Updater = container.updater()
    dispatcher = updater.dispatcher

    start_handler: CommandHandler = get_start_handler(cfg, messages)
    send_menu_command_handler: CommandHandler = get_send_menu_handler(cfg)
    personal_training_handler: CommandHandler = get_training_plan_conversation_handler(
        cfg,
        logger,
        messages,
    )
    query_handler: CallbackQueryHandler = get_callback_query_handler(
        cfg, prompts, logger, messages
    )

    send_report_handler: ConversationHandler = get_send_report_handler(
        cfg, prompts, logger, messages
    )

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(personal_training_handler)
    dispatcher.add_handler(send_report_handler)
    dispatcher.add_handler(send_menu_command_handler)
    dispatcher.add_handler(query_handler)

    logger: Logger = container.logger()
    logger.info("Starting the bot's polling...")
    updater.start_polling()

    logger.info("Bot is now in idle state.")
    updater.idle()


if __name__ == "__main__":
    main()
