from functools import wraps

from app.core import textlib as _


def is_moderator(dbuser):
    def decorator_factory(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            message = args[0]
            tg_user_id = message['from']['id']

            if dbuser.get(tg_user_id=tg_user_id).is_moderator:
                return await func(*args, **kwargs)

            return await message.reply(_.MSG_NO_RIGHTS)

        return wrapper
    return decorator_factory
