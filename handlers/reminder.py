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

@router.message(ReminderStates.text)
async def reminder_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("Введите дату и время в формате YYYY-MM-DD HH:MM (например, 2025-08-01 10:00):")
    await state.set_state(ReminderStates.remind_at)

@router.message(ReminderStates.remind_at, F.text.regexp(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$"))
async def reminder_remind_at(message: types.Message, state: FSMContext):
    try:
        remind_at = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer("Неверный формат даты. Попробуйте еще раз: YYYY-MM-DD HH:MM")
        return
    data = await state.get_data()
    user_id = message.from_user.id
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
    await message.answer(f"Напоминание добавлено: {data['text']} на {remind_at.strftime('%Y-%m-%d %H:%M')}", reply_markup=main_menu_kb())
    await state.clear()

@router.message(ReminderStates.remind_at, Command("cancel"))
@router.message(ReminderStates.remind_at, F.text.lower() == "главное меню")
async def reminder_cancel_remind_at(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

@router.message(ReminderStates.remind_at)
async def reminder_remind_at_invalid(message: types.Message):
    await message.answer("Пожалуйста, введите дату и время в формате YYYY-MM-DD HH:MM")
