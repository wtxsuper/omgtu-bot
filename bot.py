from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import *
from aiogram_calendar import SimpleCalendar, get_user_locale, SimpleCalendarCallback

import main
from messages import error

dp = Dispatcher()


class User(StatesGroup):
    group = State()
    date = State()


weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


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
    await message.answer("Выбери дату, на которую хочешь отобразить расписание:", reply_markup=await SimpleCalendar(
        locale=await get_user_locale(message.from_user)).start_calendar(year=datetime.now().year,
                                                                        month=datetime.now().month))


# simple calendar usage - filtering callbacks of calendar format
@dp.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(callback_query: CallbackQuery, callback_data: SimpleCalendarCallback) -> None:
    selected, date = await SimpleCalendar(locale=await get_user_locale(callback_query.from_user)).process_selection(
        callback_query, callback_data)
    if selected:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="Другая дата 📅", callback_data="date"))
        builder.add(InlineKeyboardButton(text="Сменить группу 🔁", callback_data="group"))
        builder.add(InlineKeyboardButton(text="Найти преподавателя 🔎", callback_data="find"))
        builder.adjust(1)
        # TODO Вывод расписания
        await callback_query.message.answer(
            f'''Расписание на {hbold(weekdays[date.weekday()].lower())}, {hbold(date.strftime("%d.%m.%Y"))}\nВ разработке...''',
            reply_markup=builder.as_markup())
        await callback_query.answer()


@dp.callback_query(F.data == "group")
async def group_change(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(User.group)
    await callback.message.answer("Введи новый номер группы:")
    await callback.answer()


@dp.callback_query(F.data == "date")
async def group_change(callback: CallbackQuery) -> None:
    await callback.message.answer("Выбери дату, на которую хочешь отобразить расписание:",
                                  reply_markup=await SimpleCalendar(
                                      locale=await get_user_locale(callback.from_user)).start_calendar(
                                      year=datetime.now().year, month=datetime.now().month))
    await callback.answer()


@dp.callback_query(F.data == "find")
async def group_change(callback: CallbackQuery) -> None:
    builder = InlineKeyboardBuilder()
    builder.button(text="Вернуться к расписанию 🔙", callback_data="date")
    await callback.message.answer("Пока ещё не реализовано...", reply_markup=builder.as_markup())
    await callback.answer()


@dp.message(Command("debug"))
async def debug(message: Message, state: FSMContext) -> None:
    if main.DEBUG_MODE == "1":
        await message.answer(f"{hbold('User ID')}: {message.from_user.id}\n"
                             f"{hbold('State')}: {await state.get_state()}\n"
                             f"{hbold('DState')}: {await state.get_data()}")
    else:
        return
