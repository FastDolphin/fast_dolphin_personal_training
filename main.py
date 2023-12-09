from telegram.ext import Updater, CommandHandler, Dispatcher
from utils import Config
from dotenv import load_dotenv
from container import Container


def main() -> None:
    load_dotenv()
    config: Config = Config()
    container: Container = Container()
    container.config.from_dict({"telegram": {"token": config.TOKEN}})
    updater: Updater = container.updater()
    dispatcher: Dispatcher = updater.dispatcher


if __name__ == "__main__":
    main()
