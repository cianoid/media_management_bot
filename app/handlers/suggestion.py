from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import app.core.textlib as _
from app.core.constants import ALLOWED_TYPES
from app.core.models import DBUser, DBSuggestion

User = DBUser()
Suggestion = DBSuggestion()


class SendSuggestion(StatesGroup):
    waiting_for_data = State()


async def remove_reply_markup(bot: Bot, message: types.Message):
    await bot.edit_message_reply_markup(
        chat_id=message.chat.id, message_id=message.message_id,
        reply_markup=None)


async def suggestion_start(message: types.Message):
    tg_user_id = message.from_user.id
    User.get_or_create(tg_user_id=tg_user_id)

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
        content = {'text': message.text}
    elif content_type == types.ContentType.DOCUMENT:
        content = {
            'file_id': message.document['file_id'],
            'file_unique_id': message.document['file_unique_id'],
            'file_size': message.document['file_size'],
            'file_name': message.document['file_name'],
            'mime_type': message.document['mime_type'],
        }
    elif content_type == types.ContentType.PHOTO:
        content = {
            'file_id': message.photo[-1].file_id,
            'file_unique_id': message.photo[-1].file_unique_id,
            'file_size': message.photo[-1].file_size,
            'caption': message.caption
        }

    Suggestion.create(
        tg_user_id=tg_user.id, content_type=content_type, content=content)

    await message.reply(_.MSG_SUGGEST_END.format(content_type_name))
    await send_data_to_moderators(message)
    await state.finish()
    # как мдератор найдет путь в записи в БД?


async def send_data_to_moderators(message: types.Message):
    tg_user = message.from_user
    text_before = 'Пользователь {} (user_id={}) предложил {}'.format(
        tg_user.username, tg_user.id, ALLOWED_TYPES[message.content_type])

    for chat_id in [209326081]:
    # for chat_id in User.get_moderator_ids():
        await message.bot.send_message(chat_id, text_before)

        buttons = [
            types.InlineKeyboardButton(
                text='Принять', callback_data='suggestion_approve'),
            types.InlineKeyboardButton(
                text='Отклонить', callback_data='suggestion_reject')
        ]
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons)
        await message.send_copy(chat_id, reply_markup=keyboard)


async def suggestion_approve(call: types.CallbackQuery):
    print(call.message)
    await remove_reply_markup(call.bot, call.message)
    await call.message.answer(
        'Модератор Вася уже <b>принял</b> это предложение')


async def suggestion_reject(call: types.CallbackQuery):
    await remove_reply_markup(call.bot, call.message)
    await call.message.answer('Вы <b>отклонили</b> предложение')

    await call.answer('Спасибо за решение! Мы сообщим пользователю результат')


def register_handlers_suggestion(dp: Dispatcher):
    dp.register_message_handler(
        suggestion_start, state='*', commands=('suggestion',))
    dp.register_message_handler(
        suggestion_data, state=SendSuggestion.waiting_for_data,
        content_types=(types.ContentType.ANY,))


def register_callbacks_suggestion(dp: Dispatcher):
    dp.register_callback_query_handler(
        suggestion_approve, text='suggestion_approve')
    dp.register_callback_query_handler(
        suggestion_reject, text='suggestion_reject')
