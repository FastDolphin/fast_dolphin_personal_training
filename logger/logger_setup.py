import os
import logging.config
from utils import Config


def init_logger(config: Config):
    log_path: str = os.path.join(config.LOG_DIR, config.LOG_FILE_NAME)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_path, "a", "utf-8")],
    )
    logger = logging.getLogger(__name__)
    return logger
