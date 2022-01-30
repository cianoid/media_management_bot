from dotenv import load_dotenv
import logging
from logging import StreamHandler, FileHandler
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import BotBlocked

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


logging.basicConfig(level=log_level)


class EnvironmentParameterError(Exception):
    pass


MODERATORS_DATA = [
    {
        'id': 2097686630,
        'username': '@Cianodi2',
        'first_name': 'first',
        'last_name': 'last'
    },
    {
        'id': 209326081,
        'username': '@Cianoid',
        'first_name': 'Cianoid',
        'last_name': ''
    }
]


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


environment_check()

bot = Bot(token=TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


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
        'command': '/moderator_list',
        'description': 'список модераторов',
        'user_access': UA_ADMIN
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


def is_admin(chat_id):
    return chat_id == ADMIN_TELEGRAM_CHAT_ID


def is_moderator(chat_id):
    return chat_id in MODERATORS.keys()


def user_start_message(chat_id):
    ua_level = UA_USER

    if is_admin(chat_id):
        ua_level = UA_ADMIN
    elif is_moderator(chat_id):
        ua_level = UA_MODERATOR

    filered_commands = [
        cmd
        for cmd in COMMANDS
        if ua_level >= cmd['user_access']
    ]

    ua_level_list = []
    for cmd in filered_commands:
        if cmd['user_access'] not in ua_level_list:
            ua_level_list.append(cmd['user_access'])

    ua_level_access_label = ua_level_list.__len__() > 1

    message_text = ''
    old_ua_level = 0

    if not ua_level_access_label:
        message_text += '\n<b>Доступные команды</b>:\n'

    for cmd in filered_commands:
        if cmd['user_access'] != old_ua_level and ua_level_access_label:
            message_text += '\n<b>Команды для {}</b>:\n'.format(
                UA_NAME[cmd['user_access']])
            old_ua_level = cmd['user_access']

        message_text += '{command} - {description}\n'.format(
            command=cmd['command'],
            description=cmd['description'])

    return message_text


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    start_message = user_start_message(message.chat.id)
    await message.reply(start_message)


@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    # print(f"Меня заблокировал пользователь!\nСообщение: {update}\n
    # Ошибка: {exception}")
    return True


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
