from aiogram import types

import core.textlib as _

ALLOWED_TYPES = {
    types.ContentType.TEXT: _.TEXT_HELP_TEXT,
    types.ContentType.PHOTO: _.TEXT_HELP_PHOTO,
    types.ContentType.DOCUMENT: _.TEXT_HELP_DOCUMENT,
}
