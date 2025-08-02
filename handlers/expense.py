from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from utils.keyboards import main_menu_kb
from database import db

router = Router()

class ExpenseStates(StatesGroup):
    amount = State()
    currency = State()
    category = State()

@router.message(Command("expense"))
@router.message(F.text == "Добавить расход")
async def start_expense(message: types.Message, state: FSMContext):
    from database import db
    await db.register_user_if_not_exists(message.from_user.id)
    await message.answer("Введите сумму расхода:")
    await state.set_state(ExpenseStates.amount)

@router.message(ExpenseStates.amount, F.text.regexp(r"^\d+(\.\d{1,2})?$"))
async def expense_amount(message: types.Message, state: FSMContext):
    await state.update_data(amount=message.text)
    from utils.keyboards import scenario_kb
    await message.answer("Выберите валюту:", reply_markup=scenario_kb(["TJS", "USD", "EUR", "RUB"]))
    await state.set_state(ExpenseStates.currency)

@router.message(ExpenseStates.amount, Command("cancel"))
@router.message(ExpenseStates.amount, F.text.lower() == "главное меню")
async def expense_cancel_amount(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

@router.message(ExpenseStates.amount)
async def expense_amount_invalid(message: types.Message):
    await message.answer("Пожалуйста, введите корректную сумму (например, 200 или 150.50)")

@router.message(ExpenseStates.currency, F.text.in_(["TJS", "USD", "EUR", "RUB"]))
async def expense_currency(message: types.Message, state: FSMContext):
    await state.update_data(currency=message.text)
    from utils.keyboards import scenario_kb
    await message.answer("Выберите категорию:", reply_markup=scenario_kb(["Еда", "Транспорт", "Коммуналка"]))
    await state.set_state(ExpenseStates.category)

@router.message(ExpenseStates.currency, Command("cancel"))
@router.message(ExpenseStates.currency, F.text.lower() == "главное меню")
async def expense_cancel_currency(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

@router.message(ExpenseStates.currency)
async def expense_currency_invalid(message: types.Message):
    await message.answer("Пожалуйста, выберите валюту из списка: TJS, USD, EUR, RUB")

@router.message(ExpenseStates.category, F.text.in_(["Еда", "Транспорт", "Коммуналка"]))
async def expense_category(message: types.Message, state: FSMContext):
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
            INSERT INTO expenses (user_id, amount, currency, category)
            VALUES ((SELECT id FROM users WHERE telegram_id=$1), $2, $3, $4)
            ON CONFLICT DO NOTHING
            """,
            user_id, amount, currency, category
        )
    await message.answer(f"Расход {amount} {currency} ({category}) добавлен!", reply_markup=main_menu_kb())
    await state.clear()

@router.message(ExpenseStates.category, Command("cancel"))
@router.message(ExpenseStates.category, F.text.lower() == "главное меню")
async def expense_cancel_category(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

@router.message(ExpenseStates.category)
async def expense_category_invalid(message: types.Message):
    await message.answer("Пожалуйста, выберите категорию из списка: Еда, Транспорт, Коммуналка")
