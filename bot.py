import asyncio
import logging
import threading

import aiogram.utils.token
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import *
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import main
from messages import error

dp = Dispatcher()


class User(StatesGroup):
    group = State()
    date = State()


async def bot_start(BOT_TOKEN: str) -> None:
    print("Для отключения бота нажмите Ctrl + C")
    try:
        # Initialize Bot instance with a default parse mode which will be passed to all API calls
        bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
        # And the run events dispatching
        await dp.start_polling(bot)
    except:
        error("Ошибка подключения к боту! Проверьте правильность токена.")
        return


@dp.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    await state.set_state(User.group)
    await message.answer(f"Привет, {message.from_user.first_name}!\n"
                         f"Это бот-помощник для студентов ОмГТУ. С моей помощью ты можешь "
                         f"узнать расписание или найти нужного преподавателя в университете.\n\n"
                         f"Для того, чтобы начать {hbold('введи номер своей группы')}. Например: ПИН-222")


@dp.message(User.group)
async def group_select(message: Message, state: FSMContext) -> None:
    # TODO Проверка на то, что такая группа действительно существует, лучше вывод клавиатуры с похожими
    await state.update_data(group=message.text)
    await state.set_state(User.date)
    await message.answer("Группа успешно выбрана!")


@dp.message(Command("change"))
async def group_change(message: Message, state: FSMContext) -> None:
    await state.set_state(User.group)
    await message.answer("Введи новый номер группы:")


@dp.message(Command("debug"))
async def debug(message: Message, state: FSMContext) -> None:
    if main.DEBUG_MODE == "1":
        await message.answer(
            f"{hbold('User ID')}: {message.from_user.id}\n"
            f"{hbold('State')}: {await state.get_state()}\n"
            f"{hbold('DState')}: {await state.get_data()}"
        )
    else:
        return
