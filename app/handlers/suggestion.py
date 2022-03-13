from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import app.textlib as _

ALLOWED_TYPES = {
    types.ContentType.TEXT: _.TEXT_HELP_TEXT,
    types.ContentType.PHOTO: _.TEXT_HELP_PHOTO,
    types.ContentType.DOCUMENT: _.TEXT_HELP_DOCUMENT,
}


class SendSuggestion(StatesGroup):
    waiting_for_data = State()


async def suggestion_start(message: types.Message):
    await message.reply(_.MSG_SUGGEST_START)
    await SendSuggestion.waiting_for_data.set()


async def suggestion_data(message: types.Message, state: FSMContext):
    if message.content_type not in ALLOWED_TYPES.keys():
        await message.reply(_.MSG_SUGGEST_START)
        return

    content_type_name = ALLOWED_TYPES[message.content_type]

    await message.reply(_.MSG_SUGGEST_END.format(content_type_name))
    await state.finish()


def register_handlers_suggestion(dp: Dispatcher):
    dp.register_message_handler(
        suggestion_start, state='*', commands=('suggestion',))
    dp.register_message_handler(
        suggestion_data, state=SendSuggestion.waiting_for_data,
        content_types=(types.ContentType.ANY,))
