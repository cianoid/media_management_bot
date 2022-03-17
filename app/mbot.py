import asyncio
import logging
import os
import re

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

import app.core.textlib as _
from app.core.exceptions import EnvironmentParameterError
from handlers.admin import (register_callbacks_admin,
                            register_handlers_admin)
from handlers.common import register_handlers_common
from handlers.suggestion import (register_callbacks_suggestion,
                                 register_handlers_suggestion)

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMINS = [
    int(chat_id)
    for chat_id
    in re.split(' +', os.getenv('ADMIN_IDS', default='0'))]

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


async def main():
    load_dotenv()
    log_init()
    environment_check()

    bot = Bot(token=TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers_common(dp)
    register_handlers_suggestion(dp)
    register_handlers_admin(dp, ADMINS)
    register_callbacks_suggestion(dp)
    register_callbacks_admin(dp)

    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
