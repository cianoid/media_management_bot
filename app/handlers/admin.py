from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import IDFilter


async def cmd_commands_admin(message: types.Message):
    await message.reply('Команды админа')


async def cmd_commands_moderator(message: types.Message):
    await message.reply('Команды модератора')


def register_handlers_admin(
        dp: Dispatcher, admin_ids: list[int], moderator_ids: list[int]):
    dp.register_message_handler(
        cmd_commands_admin, IDFilter(user_id=admin_ids), commands="commands")
    dp.register_message_handler(
        cmd_commands_moderator, IDFilter(user_id=moderator_ids),
        commands="commands")
