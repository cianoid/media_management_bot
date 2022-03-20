import logging
import os
import re

from functools import wraps
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
    logs_directory = os.path.join(os.getcwd(), 'logs')
    log_level = os.getenv('LOG_LEVEL', default='INFO')

    if not os.path.isdir(logs_directory):
        os.mkdir(logs_directory)
    filename = os.path.join(logs_directory, '%s.log' % log_level.lower())

    logging.basicConfig(
        filename=filename, filemode='a', level=log_level,
        format='%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)s - '
               '%(funcName)s()] %(message)s',
        datefmt='%d.%m.%y %T%z')

    logging.info('Logger initialized')


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


def log_entered_command(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        message = args[0]
        logger.info(_.LOG_CMD.format(message.from_user.id, message.text))

        return await func(*args, **kwargs)
    return wrapper


def log_pressed_button(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        call = args[0]
        btn_text = ''

        for btn in call.message.reply_markup.inline_keyboard[0]:
            if btn.callback_data == call.data:
                btn_text = btn.text
                break

        logger.info(
            _.LOG_BTN.format(call.from_user.id, btn_text, call.data))

        return await func(*args, **kwargs)
    return wrapper
