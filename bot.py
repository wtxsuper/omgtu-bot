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

from api import RuzAPI
from find import find_overlap
from main import DEBUG_MODE

dp = Dispatcher()
ruz = RuzAPI()


class User(StatesGroup):
    group = State()
    date = State()
    schedule = State()
    teacher = State()


digits = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


async def bot_start(BOT_TOKEN: str) -> None:
    print("Для отключения бота нажмите Ctrl + C")
    try:
        # Запуск бота с режимом парсинга HTML
        bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
        # Запуск диспетчера
        await dp.start_polling(bot)
    except:
        return


@dp.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    try:
        await state.set_state(User.group)
        await message.answer(f"Привет, {message.from_user.first_name}!\n"
                             f"Это бот-помощник для студентов ОмГТУ. С моей помощью ты можешь "
                             f"узнать расписание или найти нужного преподавателя в университете.\n\n"
                             f"Для того, чтобы начать {hbold('введи номер своей группы')}. Например: ПИН-222")
    except:
        pass


@dp.message(User.group)
async def group_select(message: Message, state: FSMContext) -> None:
    try:
        selected_group = ruz.search_group(message.text)
        if not selected_group:
            await message.answer("Не удалось найти группу, попробуйте ещё раз!")
            return
        selected_group = selected_group[0]
        await state.update_data(group=selected_group)
        await state.set_state(User.date)
        await message.answer(f"Выбрана группа {selected_group['label']}!")
        await message.answer("Выбери дату, на которую хочешь отобразить расписание:", reply_markup=await SimpleCalendar(
            locale=await get_user_locale(message.from_user)).start_calendar(year=datetime.now().year,
                                                                            month=datetime.now().month))
    except:
        await message.answer("Не удалось найти группу, попробуйте ещё раз!")
        return


@dp.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(callback_query: CallbackQuery, callback_data: SimpleCalendarCallback,
                           state: FSMContext) -> None:
    try:
        selected, date = await SimpleCalendar(locale=await get_user_locale(callback_query.from_user)).process_selection(
            callback_query, callback_data)
        if selected:
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="Другая дата 📅", callback_data="date"))
            builder.add(InlineKeyboardButton(text="Сменить группу 🔁", callback_data="group"))
            builder.add(InlineKeyboardButton(text="Найти преподавателя 🔎", callback_data="find"))
            builder.adjust(1)

            await state.update_data(date=date)
            await state.set_state(User.schedule)

            # Получение расписания
            state_data = await state.get_data()
            group = state_data.get("group")
            group_id = group.get('id')
            timetable = ruz.timetable_group(group_id, date)
            await state.update_data(schedule=timetable)

            # Вывод расписания
            await callback_query.message.answer(
                f'''Расписание на {hbold(weekdays[date.weekday()].lower())}, {hbold(date.strftime("%d.%m.%Y"))}''',
                reply_markup=builder.as_markup())
            if not timetable:
                await callback_query.message.answer("Похоже, что пар на этот день нет...")
            for lesson in timetable:
                answer = (
                    f"{digits[lesson.get('lessonNumberStart')]} {lesson.get('beginLesson')}-{lesson.get('endLesson')} "
                    f"{hbold(''.join([i[0] for i in lesson.get('kindOfWork').split(' ')]).upper())}\n"
                    f"{hbold(lesson.get('discipline'))}\n"
                    f"👨‍🏫 {lesson.get('lecturer')}\n"
                    f"📍 {lesson.get('auditorium')}\n"
                    f"🖇️ ")
                if lesson.get('stream'):
                    answer += lesson.get('stream')
                elif lesson.get('subGroup'):
                    answer += lesson.get('subGroup')
                else:
                    answer += group.get('label')
                await callback_query.message.answer(answer)
            await callback_query.answer()
    except:
        pass


@dp.callback_query(F.data == "group")
async def group_change(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await state.set_state(User.group)
        await callback.message.answer("Введи новый номер группы:")
        await callback.answer()
    except:
        pass


@dp.callback_query(F.data == "date")
async def group_change(callback: CallbackQuery) -> None:
    try:
        await callback.message.answer("Выбери дату, на которую хочешь отобразить расписание:",
                                      reply_markup=await SimpleCalendar(
                                          locale=await get_user_locale(callback.from_user)).start_calendar(
                                          year=datetime.now().year, month=datetime.now().month))
        await callback.answer()
    except:
        pass


@dp.callback_query(F.data == "find")
async def find_teacher(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.message.answer("Введи ФИО преподавателя, которого хочешь найти:")
        await state.set_state(User.teacher)
        await callback.answer()
    except:
        pass


@dp.message(User.teacher)
async def group_select(message: Message, state: FSMContext) -> None:
    selected_teacher = ruz.search_teacher(message.text)
    if not selected_teacher:
        await message.answer("Не удалось найти преподавателя, попробуйте ещё раз!")
        return
    selected_teacher = selected_teacher[0]
    await state.update_data(teacher=selected_teacher)
    await state.set_state(User.date)

    builder = InlineKeyboardBuilder()
    builder.button(text="Вернуться к расписанию 🔙", callback_data="date")
    await message.answer(f"Выбран преподаватель {selected_teacher.get('label')}!", reply_markup=builder.as_markup())

    # Получение расписания преподавателя и студента
    state_data = await state.get_data()
    date = state_data.get('date')
    teacher_schedule = ruz.timetable_teacher(selected_teacher.get('id'), date)
    student_schedule = state_data.get('schedule')

    # Нахождение пересечений расписаний
    overlaps = find_overlap(student_schedule, teacher_schedule)

    if not overlaps:
        await message.answer(
            "Похоже, что я не могу предложить тебе удобный вариант... Попробуй выбрать другую дату")

    # Вывод расписания
    for oi, overlap in enumerate(overlaps):
        answer = hbold(f'Вариант {oi + 1}\n') + f'Можно подойти {hunderline(overlap[0])} пар'
        await message.answer(answer)

        # Пара студента
        student_lesson = overlap[1]
        student_answer = (
            f"{digits[student_lesson.get('lessonNumberStart')]} {student_lesson.get('beginLesson')}-{student_lesson.get('endLesson')} "
            f"{hbold(''.join([i[0] for i in student_lesson.get('kindOfWork').split(' ')]).upper())}\n"
            f"{hbold(student_lesson.get('discipline'))}\n"
            f"👨‍🏫 {student_lesson.get('lecturer')}\n"
            f"📍 {student_lesson.get('auditorium')}\n"
            f"🖇️ ")
        if student_lesson.get('stream'):
            student_answer += student_lesson.get('stream')
        elif student_lesson.get('subGroup'):
            student_answer += student_lesson.get('subGroup')
        else:
            student_answer += student_lesson.get('group')

        # Пара преподавателя
        teacher_lesson = overlap[2]
        teacher_answer = (
            f"{digits[teacher_lesson.get('lessonNumberStart')]} {teacher_lesson.get('beginLesson')}-{teacher_lesson.get('endLesson')} "
            f"{hbold(''.join([i[0] for i in teacher_lesson.get('kindOfWork').split(' ')]).upper())}\n"
            f"{hbold(teacher_lesson.get('discipline'))}\n"
            f"👨‍🏫 {teacher_lesson.get('lecturer')}\n"
            f"📍 {teacher_lesson.get('auditorium')}\n"
            f"🖇️ ")
        if teacher_lesson.get('stream'):
            teacher_answer += teacher_lesson.get('stream')
        elif teacher_lesson.get('subGroup'):
            teacher_answer += teacher_lesson.get('subGroup')
        else:
            teacher_answer += teacher_lesson.get('group')

        # Вывод сообщений
        await message.answer(hbold('ВАША ПАРА 🎒\n\n') + student_answer)
        await message.answer(hbold('ПАРА ПРЕПОДАВАТЕЛЯ 💼\n\n') + teacher_answer)


@dp.message(Command("debug"))
async def debug(message: Message, state: FSMContext) -> None:
    if DEBUG_MODE == "1":
        await message.answer(f"{hbold('User ID')}: {message.from_user.id}\n"
                             f"{hbold('State')}: {await state.get_state()}\n"
                             f"{hbold('DState')}: {await state.get_data()}")
    else:
        return
