from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from utils.keyboards import main_menu_kb
from database import db

router = Router()

class IncomeStates(StatesGroup):
    amount = State()
    currency = State()
    category = State()

@router.message(Command("income"))
@router.message(F.text == "Добавить доход")
async def start_income(message: types.Message, state: FSMContext):
    from database import db
    await db.register_user_if_not_exists(message.from_user.id)
    await message.answer("Введите сумму дохода:")
    await state.set_state(IncomeStates.amount)

@router.message(IncomeStates.amount, F.text.regexp(r"^\d+(\.\d{1,2})?$"))
async def income_amount(message: types.Message, state: FSMContext):
    await state.update_data(amount=message.text)
    await state.update_data(currency="TJS")  # Валюта по умолчанию
    from utils.keyboards import scenario_kb
    await message.answer("Выберите категорию:", reply_markup=scenario_kb(["Зарплата", "Фриланс"]))
    await state.set_state(IncomeStates.category)

@router.message(IncomeStates.amount, Command("cancel"))
@router.message(IncomeStates.amount, F.text.lower() == "главное меню")
async def income_cancel_amount(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

@router.message(IncomeStates.amount)
async def income_amount_invalid(message: types.Message):
    await message.answer("Пожалуйста, введите корректную сумму (например, 5000 или 5000.50) или нажмите 'Главное меню' для выхода.")




@router.message(IncomeStates.category, F.text.in_(["Зарплата", "Фриланс"]))
async def income_category(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = float(data["amount"])
    currency = data["currency"]
    category = message.text
    user_id = message.from_user.id
    # Сохраняем в базу данных
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO incomes (user_id, amount, currency, category)
            VALUES ((SELECT id FROM users WHERE telegram_id=$1), $2, $3, $4)
            ON CONFLICT DO NOTHING
            """,
            user_id, amount, currency, category
        )
    await message.answer(f"Доход {amount} {currency} ({category}) добавлен!", reply_markup=main_menu_kb())
    await state.clear()

@router.message(IncomeStates.category, Command("cancel"))
@router.message(IncomeStates.category, F.text.lower() == "главное меню")
async def income_cancel_category(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

@router.message(IncomeStates.category)
async def income_category_invalid(message: types.Message):
    await message.answer("Пожалуйста, выберите категорию из списка: Зарплата, Фриланс или нажмите 'Главное меню' для выхода.")
