from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import IDFilter

from app.core import textlib as _
from app.core.models import DBUser


async def cmd_commands_admin(message: types.Message):
    await message.reply(_.MSG_ADMIN_COMMANDS)


async def cmd_moderator_list(message: types.Message):
    dbuser = DBUser()
    moderators = dbuser.get_moderator_list()
    print(moderators)

    if not moderators:
        await message.reply(_.MSG_NO_MODERATORS)
        return

    text = _.MSG_MODERATOR_LIST

    for moderator in moderators:
        print(moderator)
        text += ' - @{} (id={})\n'.format(
            moderator.tg_username, moderator.tg_user_id)

    await message.reply(text)


async def cmd_moderator_add(message: types.Message):
    await message.reply(_.MSG_ADMIN_COMMANDS)


async def cmd_moderator_delete(message: types.Message):
    await message.reply(_.MSG_ADMIN_COMMANDS)


def register_handlers_admin(dp: Dispatcher, admin_ids: list[int]):
    dp.register_message_handler(
        cmd_commands_admin, IDFilter(user_id=admin_ids), commands="commands")
    dp.register_message_handler(
        cmd_moderator_list, state='*', commands=('moderator_list',))
    dp.register_message_handler(
        cmd_moderator_add, state='*', commands=('moderator_add',))
    dp.register_message_handler(
        cmd_moderator_delete, state='*', commands=('moderator_delete',))
