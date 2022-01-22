import logging
import os
from logging import StreamHandler, FileHandler
from functools import wraps


from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler, Updater,
                          MessageHandler, Filters)

import text

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

MODERATORS_DATA = [{
    'id': 2097686630,
    'username': '@Cianodi2',
    'first_name': 'first',
    'last_name': 'last'
}, {
    'id': 209326081,
    'username': '@Cianoid',
    'first_name': 'Cianoid',
    'last_name': ''
}]


class Moderator:
    id: int
    username: str
    first_name: str
    last_name: str

    def __init__(self, moderator: dict):
        self.id = moderator['id']
        self.username = moderator['username']
        self.first_name = moderator['first_name']
        self.last_name = moderator['last_name']

    def __str__(self):
        name = self.id

        if self.first_name and self.last_name:
            name = f'{self.first_name} {self.last_name}'
        elif self.first_name:
            name = self.first_name
        elif self.last_name:
            name = self.last_name

        return f'{name} ({self.username})' if self.username else name


MODERATORS = {
    moderator['id']: Moderator(moderator) for moderator in MODERATORS_DATA
}


class EnvironmentParameterError(Exception):
    pass


def is_admin(update: Update):
    return update.effective_chat.id == ADMIN_TELEGRAM_CHAT_ID


def is_moderator(update: Update):
    return update.effective_chat.id in MODERATORS.keys()


def is_moderator_decorator(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        if is_moderator(update):
            return func(update, context, *args, **kwargs)

        update.message.reply_text('У вас нет прав модератора!')

        return False

    return wrapper


def is_admin_decorator(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        if is_admin(update):
            return func(update, context, *args, **kwargs)

        update.message.reply_text('У вас нет прав администратора!')

        return False

    return wrapper


def environment_check():
    try:
        logger.debug(text.LOG_DEBUG_ENV_CHECK)

        if TELEGRAM_TOKEN is None:
            raise EnvironmentParameterError('TELEGRAM_TOKEN')
        if ADMIN_TELEGRAM_CHAT_ID is None:
            raise EnvironmentParameterError('ADMIN_TELEGRAM_CHAT_ID')
    except EnvironmentParameterError as parameter:
        logger.critical(
            text.LOG_CRITICAL_ENV_CHECK_FAILED.format(parameter=parameter))
        raise SystemExit


UA_USER = 10
UA_MODERATOR = 20
UA_ADMIN = 30

UA_NAME = {
    UA_USER: 'Пользователь',
    UA_MODERATOR: 'Модератор',
    UA_ADMIN: 'Администратор',
}

COMMANDS = (
    {
        'command': '/start',
        'description': 'стартовое сообщение',
        'user_access': UA_USER
    },
    {
        'command': '/help',
        'description': 'помощь',
        'user_access': UA_USER
    },
    {
        'command': '/propose',
        'description': 'предложить что-нибудь',
        'user_access': UA_USER
    },
    {
        'command': '/approve',
        'description': 'одобрить предложенное пользователем',
        'user_access': UA_MODERATOR},
    {
        'command': '/decline',
        'description': 'отклонить предложенное пользователем',
        'user_access': UA_MODERATOR
    },
    {
        'command': '/moderator_add',
        'description': 'добавить модератора',
        'user_access': UA_ADMIN
    },
    {
        'command': '/moderator_delete',
        'description': 'удалить модератора',
        'user_access': UA_ADMIN
    },
)


def escape_markdown(string):
    escape_chars = '-._'

    for char_search in escape_chars:
        string = f'\\{char_search}'.join(string.split(char_search))

    return string


def user_start_message(update):
    ua_level = UA_USER

    if is_admin(update):
        ua_level = UA_ADMIN
    elif is_moderator(update):
        ua_level = UA_MODERATOR

    filered_commands = [
        cmd
        for cmd in COMMANDS
        if ua_level >= cmd['user_access']
    ]

    ua_level_access_label = [
                                cmd['user_access']
                                for cmd in filered_commands].__len__() > 1

    message_text = ''
    old_ua_level = 0

    for cmd in filered_commands:
        if cmd['user_access'] != old_ua_level and ua_level_access_label:
            message_text += '\n*Команды для {}*:\n'.format(
                escape_markdown(UA_NAME[cmd['user_access']]))
            old_ua_level = cmd['user_access']

        message_text += escape_markdown('{command} - {description}\n'.format(
            command=cmd['command'],
            description=cmd['description']))

    return message_text


def handler_propose(update: Update, context: CallbackContext):
    pass


@is_moderator_decorator
def handler_approve(update: Update, context: CallbackContext):
    pass


@is_moderator_decorator
def handler_decline(update: Update, context: CallbackContext):
    pass


@is_admin_decorator
def handler_moderator_add(update: Update, context: CallbackContext):
    pass


@is_admin_decorator
def handler_moderator_delete(update: Update, context: CallbackContext):
    pass


def handler_start(update: Update, context: CallbackContext):
    start_message = user_start_message(update)

    update.message.reply_text(
        start_message, parse_mode='MarkdownV2'
    )


def handler_help(update: Update, context: CallbackContext):
    handler_start(update, context)


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that command.")


def main():
    logger.info(text.LOG_INFO_LAUNCH)

    environment_check()

    updater = Updater(token=TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    handlers = [
        handler_name
        for handler_name in globals()
        if handler_name.startswith('handler')]

    for handler_name in handlers:
        dispatcher.add_handler(
            CommandHandler(
                handler_name.replace('handler_', ''),
                globals()[handler_name]))

    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
