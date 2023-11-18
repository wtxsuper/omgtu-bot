import asyncio
import logging
import threading

import aiogram.utils.token
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from messages import error


async def bot_start(token: str) -> None:
    logger = logging.getLogger("bot")
    logger.debug("Создан логгер для бота.")
    logger.debug("В функцию бота передан токен %s.", token)
    print("...")
    try:
        # Initialize Bot instance with a default parse mode which will be passed to all API calls
        bot = Bot(token, parse_mode=ParseMode.HTML)
        # And the run events dispatching
        dp = Dispatcher()
        await dp.start_polling(bot)
    except:
        error("Ошибка подключения к боту! Проверьте правильность токена.")
