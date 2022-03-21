from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData

import app.core.textlib as _
from app.core.constants import ALLOWED_TYPES
from app.core.common import logger, log_entered_command, log_callback_action
from app.core.decorators import is_moderator
from app.core.models import DBSuggestion, DBUser, Suggestion

ACTION_APPROVE = 1
ACTION_REJECT = 2


class SendSuggestion(StatesGroup):
    waiting_for_data = State()


async def remove_reply_markup(bot: Bot, message: types.Message):
    await bot.edit_message_reply_markup(
        chat_id=message.chat.id, message_id=message.message_id,
        reply_markup=None)


@is_moderator(db_user=DBUser())
@log_entered_command
async def suggestion_list(message: types.Message):
    suggestions = DBSuggestion().get_new_suggestion_list()
    chat_id = message.chat.id

    for suggestion in suggestions:
        text = text_for_moderated_data(
            suggestion.content_type, suggestion.user.tg_username,
            suggestion.user.tg_user_id)
        keyboard = keyboard_for_suggestion(suggestion.pk)

        await message.bot.send_message(chat_id=chat_id, text=text)

        if suggestion.content_type == types.ContentType.TEXT:
            await message.bot.send_message(
                chat_id=chat_id, text=suggestion.content_text,
                reply_markup=keyboard)
        elif suggestion.content_type == types.ContentType.PHOTO:
            await message.bot.send_photo(
                chat_id=chat_id, photo=suggestion.content_file_id,
                caption=suggestion.content_caption, reply_markup=keyboard)
        elif suggestion.content_type == types.ContentType.DOCUMENT:
            await message.bot.send_document(
                chat_id=chat_id, document=suggestion.content_file_id,
                caption=suggestion.content_caption, reply_markup=keyboard)


@log_entered_command
async def suggestion_start(message: types.Message):
    tg_user_id = message.from_user.id
    tg_username = message.from_user.username
    DBUser().get_or_create(tg_user_id=tg_user_id, tg_username=tg_username)

    await message.reply(_.MSG_SUGGEST_START)
    await SendSuggestion.waiting_for_data.set()


@log_entered_command
async def suggestion_data(message: types.Message, state: FSMContext):
    if message.content_type not in ALLOWED_TYPES.keys():
        await message.reply(_.MSG_SUGGEST_START)
        return

    tg_user = message.from_user
    content_type = message.content_type
    content_type_name = ALLOWED_TYPES[message.content_type]

    content = {}

    if content_type == types.ContentType.TEXT:
        logger.info(
            _.LOG_CMD_SUGGESTION_TEXT.format(
                message.from_user.id, message.text))

        content = {
            'content_text': message.text,
            'tg_message_id': message.message_id
        }
    elif content_type == types.ContentType.DOCUMENT:
        file_id = message.document['file_id']
        file_unique_id = message.document['file_unique_id']

        logger.info(
            _.LOG_CMD_SUGGESTION_PHOTO.format(
                message.from_user.id, file_id, file_unique_id,
                message.caption))

        content = {
            'content_file_id': file_id,
            'content_file_unique_id': file_unique_id,
            'content_file_size': message.document['file_size'],
            'content_file_name': message.document['file_name'],
            'content_mime_type': message.document['mime_type'],
            'content_caption': message.caption,
            'tg_message_id': message.message_id
        }
    elif content_type == types.ContentType.PHOTO:
        file_id = message.photo[-1].file_id
        file_unique_id = message.photo[-1].file_unique_id

        logger.info(
            _.LOG_CMD_SUGGESTION_PHOTO.format(
                message.from_user.id, file_id, file_unique_id,
                message.caption))

        content = {
            'content_file_id': file_id,
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


def keyboard_for_suggestion(suggestion_id):
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

    return keyboard


def text_for_moderated_data(content_type, username, userid):
    return _.MSG_USER_SUGGEST.format(
        username, userid, ALLOWED_TYPES[content_type])


async def send_data_to_moderators(message: types.Message, suggestion_id):
    text = text_for_moderated_data(
        message.content_type, message.from_user.username, message.from_user.id)

    for chat_id in DBUser().get_moderator_ids():
        await message.bot.send_message(chat_id, text)
        await message.send_copy(
            chat_id, reply_markup=keyboard_for_suggestion(suggestion_id))


@log_callback_action
async def suggestion_proceed(call: types.CallbackQuery, callback_data: dict):
    suggestion_id = callback_data.get('suggestion_id', None)
    action = int(callback_data.get('action', '0'))

    if suggestion_id is None or action not in (ACTION_REJECT, ACTION_APPROVE):
        logger.error(
            _.LOG_BTN_NO_SUGGESTIONID
            if suggestion_id is None
            else _.LOG_BTN_NO_ACTION)

        await call.answer(_.MSG_SMTH_IS_WRONG)
        return

    suggestion = DBSuggestion().get(pk=suggestion_id)

    if suggestion.status in (
            Suggestion.STATUS_APPROVED, Suggestion.STATUS_REJECTED):
        logger.warning(
            (_.LOG_SUGGESTION_BEEN_APPROVED
             if action == ACTION_APPROVE
             else _.LOG_SUGGESTION_BEEN_REJECTED).format(suggestion_id))

        await remove_reply_markup(call.bot, call.message)
        await call.message.answer(
            _.MSG_MODERATION_HAS_ALREADY_TAKEN_PLACE.format(
                suggestion.user.tg_username, suggestion.moderation_date))
        return

    target_status = Suggestion.STATUS_APPROVED \
        if action == ACTION_APPROVE \
        else Suggestion.STATUS_REJECTED

    update_data = {
        'moderation_date': datetime.utcnow(),
        'tg_moderator_id': call.message.from_user.id,
        'status': target_status
    }

    if DBSuggestion().update(pk=suggestion_id, update_data=update_data):
        if action == ACTION_APPROVE:
            text_moderation_ok_moderator = _.MSG_APPROVE_MODERATOR
            text_moderation_ok_user = _.MSG_APPROVE_USER
            text_log = _.LOG_SUGGESTION_APPROVED
        else:
            text_moderation_ok_moderator = _.MSG_REJECT_MODERATOR
            text_moderation_ok_user = _.MSG_REJECT_USER
            text_log = _.LOG_SUGGESTION_REJECTED

        logger.info(text_log.format(suggestion.moderator, suggestion_id))

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
        suggestion_list, commands="suggestion_list")
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
