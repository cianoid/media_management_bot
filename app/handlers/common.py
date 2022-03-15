from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from app.core.models import DBUser

User = DBUser()


def user_start_message(user_id):
    return 'Привет!'


async def cmd_cancel(message: types.Message, state: FSMContext):
    await message.reply(
        'ОК! Если что-то захотите прислать, просто введите команду '
        '/suggest снова')
    await state.finish()


async def cmd_start(message: types.Message):
    tg_user_id = message.from_user.id
    start_message = user_start_message(tg_user_id)

    User.get_or_create(tg_user_id=tg_user_id)
    await message.reply(start_message)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(
        cmd_start, commands=('start', 'help'), state='*')
    dp.register_message_handler(
        cmd_cancel, commands='cancel', state='*')
    dp.register_message_handler(
        cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
