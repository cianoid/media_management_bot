from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import IDFilter
from aiogram.utils.callback_data import CallbackData

from app.core import textlib as _
from app.core.models import DBUser


async def cmd_commands_admin(message: types.Message):
    await message.reply(_.MSG_ADMIN_COMMANDS)


cb_moderator_delete = CallbackData('moderator_delete', 'tg_user_id')


async def cmd_moderator_list(message: types.Message):
    moderators = DBUser().get_moderator_list()

    if not moderators:
        await message.reply(_.MSG_NO_MODERATORS)
        return

    text = _.MSG_MODERATOR_LIST
    buttons = list()

    for moderator in moderators:
        text += ' - ' + str(moderator) + '\n'
        buttons.append(
            types.InlineKeyboardButton(
                text='Удалить {}'.format(
                    moderator),
                callback_data=cb_moderator_delete.new(
                    tg_user_id=moderator.tg_user_id)),
        )

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)

    await message.reply(text, reply_markup=keyboard)


async def cmd_moderator_add(message: types.Message):
    print(message.text)

    await message.reply(_.MSG_ADMIN_COMMANDS)


async def moderator_delete(call: types.CallbackQuery, callback_data: dict):
    tg_user_id = callback_data.get('tg_user_id', None)

    if tg_user_id is None:
        await call.answer(_.MSG_SMTH_IS_WRONG)
        return False

    user = DBUser().get(tg_user_id=tg_user_id)

    if not user.is_moderator:
        await call.message.answer('{} уже не модератор'.format(user))
        return False

    updata = {
        'is_moderator': False
    }

    if DBUser().update(tg_user_id=tg_user_id, update_data=updata):
        await call.message.reply('{} больше не модератор'.format(user))
        return True

    return False


def register_handlers_admin(dp: Dispatcher, admin_ids: list[int]):
    dp.register_message_handler(
        cmd_commands_admin, IDFilter(user_id=admin_ids), commands="commands")
    dp.register_message_handler(
        cmd_moderator_list, state='*', commands=('moderator_list',))
    dp.register_message_handler(
        cmd_moderator_add, state='*', commands=('moderator_add',))


def register_callbacks_admin(dp: Dispatcher):
    dp.register_callback_query_handler(
        moderator_delete, cb_moderator_delete.filter())
