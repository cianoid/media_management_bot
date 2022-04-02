from aiogram.types import BotCommand

from core import textlib as _


USER_COMMANDS = [
    BotCommand(_.CMD_NAME_HELP, _.CMD_DESC_HELP),
    BotCommand(_.CMD_NAME_ME, _.CMD_DESC_ME),
    BotCommand(_.CMD_NAME_SUGGESTION, _.CMD_DESC_SUGGESTION),
]

MODERATOR_COMMANDS = [
    BotCommand(_.CMD_NAME_SUGGESTION_LIST, _.CMD_DESC_SUGGESTION_LIST),
]

ADMIN_COMMANDS = [
    BotCommand(_.CMD_NAME_MODERATOR_LIST, _.CMD_DESC_MODERATOR_LIST),
    BotCommand(_.CMD_NAME_MODERATOR_ADD, _.CMD_DESC_MODERATOR_ADD),
]
