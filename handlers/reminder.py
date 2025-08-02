from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from utils.keyboards import main_menu_kb
from database import db
from datetime import datetime

router = Router()

class ReminderStates(StatesGroup):
    text = State()
    remind_at = State()

@router.message(Command("reminder"))
@router.message(F.text == "Создать напоминание")
async def start_reminder(message: types.Message, state: FSMContext):
    from database import db
    await db.register_user_if_not_exists(message.from_user.id)
    await message.answer("Введите текст напоминания:")
    await state.set_state(ReminderStates.text)

@router.message(ReminderStates.text, Command("cancel"))
@router.message(ReminderStates.text, F.text.lower() == "главное меню")
async def reminder_cancel_text(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

from aiogram_calendar import SimpleCalendar, get_user_locale
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@router.message(ReminderStates.text)
async def reminder_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    # Показываем календарь для выбора даты
    await message.answer(
        "Выберите дату:",
        reply_markup=await SimpleCalendar(locale=await get_user_locale(message.from_user)).start_calendar()
    )
    await state.set_state(ReminderStates.remind_at)

from aiogram.types import CallbackQuery

@router.callback_query(ReminderStates.remind_at)
async def process_calendar(callback: CallbackQuery, state: FSMContext):
    from aiogram_calendar import SimpleCalendar, get_user_locale
    selected, date = await SimpleCalendar(locale=await get_user_locale(callback.from_user)).process_selection(callback, callback.data)
    if selected:
        await state.update_data(date=date)
        # После выбора даты — показываем клавиатуру времени (часы)
        hours_kb = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text=f"{h:02d}:00", callback_data=f"set_hour_{h}") for h in range(8, 21)
            ]]
        )
        await callback.message.answer("Выберите время:", reply_markup=hours_kb)
        await callback.answer()
    else:
        await callback.answer()

@router.callback_query(ReminderStates.remind_at, F.data.regexp(r"set_hour_\d{1,2}"))
async def process_hour(callback: CallbackQuery, state: FSMContext):
    import re
    hour = int(re.search(r"set_hour_(\d{1,2})", callback.data).group(1))
    # После выбора часа — показываем клавиатуру минут
    minutes_kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=f"{minute:02d}", callback_data=f"set_minute_{hour}_{minute}") for minute in (0, 15, 30, 45)
        ]]
    )
    await callback.message.answer("Выберите минуты:", reply_markup=minutes_kb)
    await callback.answer()

@router.callback_query(ReminderStates.remind_at, F.data.regexp(r"set_minute_\d{1,2}_\d{1,2}"))
async def process_minute(callback: CallbackQuery, state: FSMContext):
    import re
    match = re.search(r"set_minute_(\d{1,2})_(\d{1,2})", callback.data)
    hour = int(match.group(1))
    minute = int(match.group(2))
    data = await state.get_data()
    date = data.get("date")
    remind_at = date.replace(hour=hour, minute=minute, second=0)
    user_id = callback.from_user.id
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO reminders (user_id, text, remind_at)
            VALUES ((SELECT id FROM users WHERE telegram_id=$1), $2, $3)
            ON CONFLICT DO NOTHING
            """,
            user_id, data["text"], remind_at
        )
    await callback.message.answer(f"Напоминание добавлено: {data['text']} на {remind_at.strftime('%Y-%m-%d %H:%M')}", reply_markup=main_menu_kb())
    await state.clear()
    await callback.answer()

@router.message(ReminderStates.remind_at, Command("cancel"))
@router.message(ReminderStates.remind_at, F.text.lower() == "главное меню")
async def reminder_cancel_remind_at(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

