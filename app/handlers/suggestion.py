from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import IDFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData

import app.core.textlib as _
from app.core.constants import ALLOWED_TYPES
from app.core.models import DBUser, DBSuggestion, Suggestion

ACTION_APPROVE = 1
ACTION_REJECT = 2


class SendSuggestion(StatesGroup):
    waiting_for_data = State()


async def remove_reply_markup(bot: Bot, message: types.Message):
    await bot.edit_message_reply_markup(
        chat_id=message.chat.id, message_id=message.message_id,
        reply_markup=None)


async def suggestion_list(message: types.Message):
    # проверка на модератора
    await message.reply('Ща все будет')


async def suggestion_start(message: types.Message):
    tg_user_id = message.from_user.id
    tg_username = message.from_user.username
    DBUser().get_or_create(tg_user_id=tg_user_id, tg_username=tg_username)

    await message.reply(_.MSG_SUGGEST_START)
    await SendSuggestion.waiting_for_data.set()


async def suggestion_data(message: types.Message, state: FSMContext):
    if message.content_type not in ALLOWED_TYPES.keys():
        await message.reply(_.MSG_SUGGEST_START)
        return

    tg_user = message.from_user
    content_type = message.content_type
    content_type_name = ALLOWED_TYPES[message.content_type]

    content = {}

    if content_type == types.ContentType.TEXT:
        content = {
            'content_text': message.text,
            'tg_message_id': message.message_id
        }
    elif content_type == types.ContentType.DOCUMENT:
        content = {
            'content_file_id': message.document['file_id'],
            'content_file_unique_id': message.document['file_unique_id'],
            'content_file_size': message.document['file_size'],
            'content_file_name': message.document['file_name'],
            'content_mime_type': message.document['mime_type'],
            'content_caption': message.caption,
            'tg_message_id': message.message_id
        }
    elif content_type == types.ContentType.PHOTO:
        content = {
            'content_file_id': message.photo[-1].file_id,
            'content_file_unique_id': message.photo[-1].file_unique_id,
            'content_file_size': message.photo[-1].file_size,
            'content_caption': message.caption,
            'tg_message_id': message.message_id
        }

    content.update({'content_type': content_type})

    suggestion_id = DBSuggestion().create(tg_user_id=tg_user.id, **content)

    await message.reply(_.MSG_SUGGEST_END.format(content_type_name))
    await send_data_to_moderators(message, suggestion_id)
    await state.finish()


cb_suggestion_approve = CallbackData('suggestion', 'action', 'suggestion_id')
cb_suggestion_reject = CallbackData('suggestion', 'action', 'suggestion_id')


async def send_data_to_moderators(message: types.Message, suggestion_id):
    tg_user = message.from_user
    text_before = _.MSG_USER_SUGGEST.format(
        tg_user.username, tg_user.id, ALLOWED_TYPES[message.content_type])

    for chat_id in DBUser().get_moderator_ids():
        await message.bot.send_message(chat_id, text_before)

        buttons = [
            types.InlineKeyboardButton(
                text=_.BTN_APPROVE,
                callback_data=cb_suggestion_approve.new(
                    action=ACTION_APPROVE, suggestion_id=suggestion_id)),
            types.InlineKeyboardButton(
                text=_.BTN_REJECT,
                callback_data=cb_suggestion_reject.new(
                    action=ACTION_REJECT, suggestion_id=suggestion_id)),
        ]

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        await message.send_copy(chat_id, reply_markup=keyboard)


async def suggestion_proceed(call: types.CallbackQuery, callback_data: dict):
    suggestion_id = callback_data.get('suggestion_id', None)
    action = int(callback_data.get('action', '0'))

    if suggestion_id is None or action not in (ACTION_REJECT, ACTION_APPROVE):
        await call.answer(_.MSG_SMTH_IS_WRONG)
        return

    suggestion = DBSuggestion().get(pk=suggestion_id)

    if suggestion.status in (
            Suggestion.STATUS_APPROVED, Suggestion.STATUS_REJECTED):
        await remove_reply_markup(call.bot, call.message)
        await call.message.answer(
            _.MSG_MODERATION_HAS_ALREADY_TAKEN_PLACE.format(
                suggestion.user.tg_username, suggestion.moderation_date))
        return

    if action == ACTION_APPROVE:
        target_status = Suggestion.STATUS_APPROVED
    else:
        target_status = Suggestion.STATUS_REJECTED

    update_data = {
        'moderation_date': datetime.utcnow(),
        'tg_moderator_id': call.message.from_user.id,
        'status': target_status
    }

    if DBSuggestion().update(pk=suggestion_id, update_data=update_data):
        if action == ACTION_APPROVE:
            text_moderation_ok_moderator = _.MSG_APPROVE_MODERATOR
            text_moderation_ok_user = _.MSG_APPROVE_USER
        else:
            text_moderation_ok_moderator = _.MSG_REJECT_MODERATOR
            text_moderation_ok_user = _.MSG_REJECT_USER

        await remove_reply_markup(call.bot, call.message)
        await call.message.reply(
            text_moderation_ok_moderator.format(
                suggestion.user.tg_username, suggestion.moderation_date))
        await call.bot.send_message(
            chat_id=suggestion.tg_user_id,
            reply_to_message_id=suggestion.tg_message_id,
            text=text_moderation_ok_user)
        return


def register_handlers_suggestion(dp: Dispatcher):
    dp.register_message_handler(
        suggestion_list, IDFilter(user_id=DBUser().get_moderator_ids()), commands="suggestion_list")
    dp.register_message_handler(
        suggestion_start, state='*', commands=('suggestion',))
    dp.register_message_handler(
        suggestion_data, state=SendSuggestion.waiting_for_data,
        content_types=(types.ContentType.ANY,))


def register_callbacks_suggestion(dp: Dispatcher):
    dp.register_callback_query_handler(
        suggestion_proceed, cb_suggestion_approve.filter())
    dp.register_callback_query_handler(
        suggestion_proceed, cb_suggestion_reject.filter())
