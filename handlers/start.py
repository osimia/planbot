from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()

from database import db

@router.message(CommandStart())
async def cmd_start(message: types.Message, state):
    await state.clear()
    await db.register_user_if_not_exists(message.from_user.id)
    from utils.keyboards import main_menu_kb
    await message.answer("Добро пожаловать в MyPlan! Управляйте своими финансами удобно и безопасно.", reply_markup=main_menu_kb())

@router.message(lambda m: m.text and m.text.lower() == "главное меню")
async def main_menu_handler(message: types.Message, state):
    await state.clear()
    from utils.keyboards import main_menu_kb
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

from aiogram.types import InputFile
import io
from database import db
from utils.excel_export import generate_excel_report
import pandas as pd

@router.message(lambda m: m.text == "Статистика")
async def statistics_handler(message: types.Message, state):
    user_id = message.from_user.id
    pool = await db.get_pool()
    async with pool.acquire() as conn:
        # Получаем доходы и расходы пользователя
        incomes = await conn.fetch("""
            SELECT amount, currency, category, created_at
            FROM incomes WHERE user_id=(SELECT id FROM users WHERE telegram_id=$1)
            ORDER BY created_at
        """, user_id)
        expenses = await conn.fetch("""
            SELECT amount, currency, category, created_at
            FROM expenses WHERE user_id=(SELECT id FROM users WHERE telegram_id=$1)
            ORDER BY created_at
        """, user_id)
    # Преобразуем в list[dict]
    incomes_list = [dict(rec) for rec in incomes]
    expenses_list = [dict(rec) for rec in expenses]
    # Считаем баланс
    total_income = sum(float(i["amount"]) for i in incomes_list)
    total_expense = sum(float(e["amount"]) for e in expenses_list)
    balance = total_income - total_expense
    # Группировка по месяцам
    def group_by_month(data):
        if not data:
            return {}
        df = pd.DataFrame(data)
        df["Месяц"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m")
        return df.groupby("Месяц")["amount"].sum().to_dict()
    income_by_month = group_by_month(incomes_list)
    expense_by_month = group_by_month(expenses_list)
    # Формируем текст отчета
    report_lines = [f"Ваш текущий баланс: <b>{balance:.2f}</b>", "\n<b>Доходы по месяцам:</b>"]
    for m, v in income_by_month.items():
        report_lines.append(f"{m}: {v:.2f}")
    report_lines.append("\n<b>Расходы по месяцам:</b>")
    for m, v in expense_by_month.items():
        report_lines.append(f"{m}: {v:.2f}")
    report_text = "\n".join(report_lines)
    await message.answer(report_text, parse_mode="HTML")
    # Генерируем Excel и отправляем
    excel_file = await generate_excel_report(user_id, incomes_list, expenses_list)
    await message.answer_document(InputFile(excel_file, filename="finance_report.xlsx"), caption="Скачать полный отчет в Excel")

@router.message(lambda m: m.text == "Советы")
async def tips_handler(message: types.Message, state):
    # Можно сделать случайный совет или список советов
    await message.answer("Совет: Покупайте овощи на базаре вечером — так дешевле!\n\nСледите за своими расходами и ставьте финансовые цели.")
