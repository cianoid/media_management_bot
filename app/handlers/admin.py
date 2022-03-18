import re

from aiogram import Dispatcher, types
from aiogram.utils.callback_data import CallbackData

from app.core import textlib as _
from app.core.common import logger
from app.core.models import DBUser

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
    data = re.split(r' +', message.text)

    try:
        tg_user_id = data[1]
    except IndexError:
        await message.reply(_.MSG_NO_ID)
        return

    user = DBUser().get(tg_user_id=tg_user_id)

    if not user:
        await message.reply(_.MSG_USER_NOT_IN_DB)
        return

    if user.is_moderator:
        await message.answer(_.MSG_USER_ALREADY_MODERATOR.format(user))
        return

    update_data = {
        'is_moderator': True
    }

    if DBUser().update(tg_user_id=tg_user_id, update_data=update_data):
        await message.reply(_.MSG_USER_NOW_MODERATOR.format(user))
        await message.bot.send_message(
            user.tg_user_id, text=_.MSG_UR_MODERATOR)
        return


async def moderator_delete(call: types.CallbackQuery, callback_data: dict):
    tg_user_id = callback_data.get('tg_user_id', None)

    if tg_user_id is None:
        await call.answer(_.MSG_SMTH_IS_WRONG)
        return

    user = DBUser().get(tg_user_id=tg_user_id)

    if not user.is_moderator:
        await call.message.answer(
            _.MSG_USER_ALREADY_NOT_MODERATOR.format(user))
        return

    update_data = {
        'is_moderator': False
    }

    if DBUser().update(tg_user_id=tg_user_id, update_data=update_data):
        await call.message.reply(_.MSG_USER_NOW_NOT_MODERATOR.format(user))
        await call.bot.send_message(
            user.tg_user_id, text=_.MSG_UR_NOT_MODERATOR)
        return


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(
        cmd_moderator_list, state='*', commands=('moderator_list',))
    dp.register_message_handler(
        cmd_moderator_add, state='*', commands=('moderator_add',))


def register_callbacks_admin(dp: Dispatcher):
    dp.register_callback_query_handler(
        moderator_delete, cb_moderator_delete.filter())
