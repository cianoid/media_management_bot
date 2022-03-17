import logging
import os
import re

from dotenv import load_dotenv

import app.core.textlib as _
from app.core.exceptions import EnvironmentParameterError

load_dotenv()


ADMINS = [
    int(chat_id)
    for chat_id
    in re.split(' +', os.getenv('ADMIN_IDS', default='0'))]
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

logger = logging.getLogger(__name__)


def log_init():
    log_level = os.getenv('LOG_LEVEL', default='INFO')
    level = getattr(logging, log_level)

    logs_directory = os.path.join(os.getcwd(), 'logs')
    file_path = os.path.join(logs_directory, '%s.log' % log_level.lower())

    if not os.path.isdir(logs_directory):
        os.mkdir(logs_directory)

    formatter = logging.Formatter(
        '%(asctime)s %(name)s [%(levelname)s] %(message)s')
    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(file_path, 'a+')

    logger.setLevel(level)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logging.basicConfig(level=log_level)


def environment_check():
    try:
        logger.debug(_.LOG_DEBUG_ENV_CHECK)

        if TELEGRAM_TOKEN is None:
            raise EnvironmentParameterError('TELEGRAM_TOKEN')
        if ADMINS is None:
            raise EnvironmentParameterError('ADMIN_IDS')
    except EnvironmentParameterError as parameter:
        logger.critical(
            _.LOG_CRITICAL_ENV_CHECK_FAILED.format(parameter=parameter))
        raise SystemExit


def is_admin(tg_user_id):
    return tg_user_id in ADMINS
