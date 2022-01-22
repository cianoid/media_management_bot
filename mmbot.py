import logging
import os
from logging import StreamHandler, FileHandler

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler, Updater,
                          MessageHandler, Filters)



load_dotenv()

log_level = os.getenv('LOG_LEVEL')

try:
    level = getattr(logging, log_level)
except AttributeError:
    log_level = 'INFO'
    level = getattr(logging, log_level)

logs_directory = os.path.join(os.getcwd(), 'logs')
file_path = os.path.join(logs_directory, '%s.log' % log_level.lower())

if not os.path.isdir(logs_directory):
    os.mkdir(logs_directory)

logger = logging.getLogger()
formatter = logging.Formatter(
    '%(asctime)s %(name)s [%(levelname)s] %(message)s')
stream_handler = StreamHandler()
file_handler = FileHandler(file_path, 'a+')

logger.setLevel(level)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_TELEGRAM_CHAT_ID = int(os.getenv('ADMIN_TELEGRAM_CHAT_ID'))

LOG_CRITICAL_ENV_CHECK_FAILED = ('Отсутствует обязательная переменная '
                                 '"{parameter}". Бот остановлен')
LOG_DEBUG_ENV_CHECK = 'Проверка env-переменных для подключения'
LOG_INFO_LAUNCH = 'Бот запущен!'


class EnvironmentParameterError(Exception):
    pass


def environment_check():
    try:
        logger.debug(LOG_DEBUG_ENV_CHECK)

        if TELEGRAM_TOKEN is None:
            raise EnvironmentParameterError('TELEGRAM_TOKEN')
        if ADMIN_TELEGRAM_CHAT_ID is None:
            raise EnvironmentParameterError('ADMIN_TELEGRAM_CHAT_ID')
    except EnvironmentParameterError as parameter:
        logger.critical(
            LOG_CRITICAL_ENV_CHECK_FAILED.format(parameter=parameter))
        raise SystemExit


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello")


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.")


def main():
    logger.info(LOG_INFO_LAUNCH)

    environment_check()

    updater = Updater(token=TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
