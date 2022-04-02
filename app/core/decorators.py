from functools import wraps

from core import textlib as _
from core.common import is_moderator as is_moderator_func
from core.common import is_admin as is_admin_func


def is_moderator(db_user):
    def decorator_factory(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            message = args[0]
            tg_user = message['from']

            user = db_user.get_or_create(
                tg_user_id=tg_user['id'], tg_username=tg_user['username'])

            if is_moderator_func(user):
                return await func(*args, **kwargs)

            return await message.reply(_.MSG_NO_RIGHTS)

        return wrapper
    return decorator_factory


def is_admin(db_user):
    def decorator_factory(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            message = args[0]
            tg_user = message['from']

            user = db_user.get_or_create(
                tg_user_id=tg_user['id'], tg_username=tg_user['username'])

            if is_admin_func(user.tg_user_id):
                return await func(*args, **kwargs)

            return await message.reply(_.MSG_NO_RIGHTS)

        return wrapper
    return decorator_factory


def only_private_messages(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        data = args[0]
        message = data.message if 'message' in data else data
        message_type = message.chat.type

        if message_type == 'private':
            return await func(*args, **kwargs)

        return await message.reply(_.MSG_ONLY_PRIVATE)

    return wrapper
