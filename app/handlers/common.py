from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text


def user_start_message(chat_id):
    return 'Привет!'


async def cmd_cancel(message: types.Message, state: FSMContext):
    await message.reply(
        'ОК! Если что-то захотите прислать, просто введите команду '
        '/suggest снова')
    await state.finish()


async def cmd_start(message: types.Message):
    start_message = user_start_message(message.chat.id)
    await message.reply(start_message)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(
        cmd_start, commands=('start', 'help'), state='*')
    dp.register_message_handler(
        cmd_cancel, commands='cancel', state='*')
    dp.register_message_handler(
        cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")
