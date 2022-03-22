import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from core.common import TELEGRAM_TOKEN, environment_check, log_init
from handlers.admin import (register_callbacks_admin,
                            register_handlers_admin)
from handlers.common import register_handlers_common
from handlers.suggestion import (register_callbacks_suggestion,
                                 register_handlers_suggestion)


async def main():
    log_init()
    environment_check()

    bot = Bot(token=TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot, storage=MemoryStorage())

    register_handlers_common(dp)
    register_handlers_suggestion(dp)
    register_handlers_admin(dp)
    register_callbacks_suggestion(dp)
    register_callbacks_admin(dp)

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
