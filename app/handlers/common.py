from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.core.models import DBUser
from app.core import textlib as _


def user_start_message(user_id):
    return 'Привет!'


async def cmd_cancel(message: types.Message, state: FSMContext):
    await message.reply(_.MSG_SUGGEST_CANCEL)
    await state.finish()


async def cmd_start(message: types.Message):
    tg_user_id = message.from_user.id
    tg_username = message.from_user.username
    start_message = user_start_message(tg_user_id)

    DBUser().get_or_create(tg_user_id=tg_user_id, tg_username=tg_username)
    await message.reply(start_message, reply_markup=None)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(
        cmd_start, commands=('start', 'help'), state='*')
    dp.register_message_handler(
        cmd_cancel, commands='cancel', state='*')
    dp.register_message_handler(
        cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
