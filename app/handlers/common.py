from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from core import textlib as _
from core.common import is_admin, log_user_action
from core.decorators import only_private_messages
from core.models import DBUser


def user_start_message(from_user):
    text = _.MSG_START

    if is_admin(from_user.id):
        text += _.MSG_ADMIN_COMMANDS

    user = DBUser().get_or_create(
        tg_user_id=from_user.id, tg_username=from_user.username)

    if user.is_moderator:
        text += _.MSG_MODERATOR_COMMANDS

    text += _.MSG_USER_COMMANDS

    return text


@log_user_action
@only_private_messages
async def cmd_cancel(message: types.Message, state: FSMContext):
    await message.reply(_.MSG_SUGGEST_CANCEL)
    await state.finish()


@log_user_action
@only_private_messages
async def cmd_me(message: types.Message):
    user = message.from_user

    text = _.MSG_ABOUT + '\n<b>ID</b>: {}'.format(user.id)

    if user.username:
        text += '\n<b>Username</b>: @{}'.format(user.username)
    if user.full_name:
        text += '\n<b>Имя</b>: {}'.format(user.full_name)

    await message.reply(text)


@log_user_action
@only_private_messages
async def cmd_start(message: types.Message):
    tg_user_id = message.from_user.id
    tg_username = message.from_user.username
    start_message = user_start_message(message.from_user)

    DBUser().get_or_create(tg_user_id=tg_user_id, tg_username=tg_username)

    await message.reply(start_message, reply_markup=None)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_me, commands='me', state='*')
    dp.register_message_handler(
        cmd_start, commands=('start', 'help'), state='*')
    dp.register_message_handler(cmd_cancel, commands='cancel', state='*')
    dp.register_message_handler(
        cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
