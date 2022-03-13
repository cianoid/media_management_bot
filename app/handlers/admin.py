from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import IDFilter


async def cmd_commands_admin(message: types.Message):
    await message.reply('Команды админа')


def register_handlers_admin(dp: Dispatcher, admin_ids: list[int]):
    dp.register_message_handler(
        cmd_commands_admin, IDFilter(user_id=admin_ids), commands="commands")
