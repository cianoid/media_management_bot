from functools import wraps

from app.core import textlib as _


def is_moderator(db_user):
    def decorator_factory(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            message = args[0]
            tg_user_id = message['from']['id']

            if db_user.get(tg_user_id=tg_user_id).is_moderator:
                return await func(*args, **kwargs)

            return await message.reply(_.MSG_NO_RIGHTS)

        return wrapper
    return decorator_factory


def only_private_messages(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        message_type = None
        message = None

        try:
            message = args[0]
            message_type = args[0]['chat']['type']
        except KeyError:
            message = args[0]['message']
            message_type = message['chat']['type']
        finally:
            if message_type == 'private':
                return await func(*args, **kwargs)

            return await message.reply(_.MSG_ONLY_PRIVATE)

    return wrapper
