import asyncio

from dotenv import load_dotenv
import logging
from logging import StreamHandler, FileHandler
import os
import re

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from exceptions import EnvironmentParameterError

from handlers.common import register_handlers_common

import text

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMINS = [
    int(chat_id)
    for chat_id
    in re.split(' +', os.getenv('ADMIN_TELEGRAM_CHAT_IDS', default='0'))]

logger = logging.getLogger(__name__)


def environment_check():
    try:
        logger.debug(text.LOG_DEBUG_ENV_CHECK)

        if TELEGRAM_TOKEN is None:
            raise EnvironmentParameterError('TELEGRAM_TOKEN')
        if ADMINS is None:
            raise EnvironmentParameterError('ADMIN_TELEGRAM_CHAT_IDS')
    except EnvironmentParameterError as parameter:
        logger.critical(
            text.LOG_CRITICAL_ENV_CHECK_FAILED.format(parameter=parameter))
        raise SystemExit


def log_init():
    log_level = os.getenv('LOG_LEVEL', default='INFO')
    level = getattr(logging, log_level)

    logs_directory = os.path.join(os.getcwd(), 'logs')
    file_path = os.path.join(logs_directory, '%s.log' % log_level.lower())

    if not os.path.isdir(logs_directory):
        os.mkdir(logs_directory)

    formatter = logging.Formatter(
        '%(asctime)s %(name)s [%(levelname)s] %(message)s')
    stream_handler = StreamHandler()
    file_handler = FileHandler(file_path, 'a+')

    logger.setLevel(level)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logging.basicConfig(level=log_level)


async def main():
    load_dotenv()
    log_init()
    environment_check()

    bot = Bot(token=TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot, storage=MemoryStorage())
    register_handlers_common(dp)

    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
