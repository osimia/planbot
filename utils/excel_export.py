import io
import pandas as pd
from datetime import datetime

async def generate_excel_report(user_id: int, incomes: list, expenses: list) -> io.BytesIO:
    """
    Создает Excel-файл с доходами и расходами пользователя по месяцам.
    :param user_id: Telegram user id
    :param incomes: список доходов (dict с amount, currency, category, created_at)
    :param expenses: список расходов (dict с amount, currency, category, created_at)
    :return: BytesIO с Excel-файлом
    """
    # Преобразуем данные в DataFrame
    df_incomes = pd.DataFrame(incomes)
    df_expenses = pd.DataFrame(expenses)
    
    # Добавим столбец 'Месяц'
    if not df_incomes.empty:
        df_incomes['Месяц'] = pd.to_datetime(df_incomes['created_at']).dt.to_period('M')
    if not df_expenses.empty:
        df_expenses['Месяц'] = pd.to_datetime(df_expenses['created_at']).dt.to_period('M')
    
    # Группировка по месяцам
    incomes_by_month = df_incomes.groupby('Месяц').agg({'amount': 'sum'}).rename(columns={'amount': 'Доход'}) if not df_incomes.empty else pd.DataFrame()
    expenses_by_month = df_expenses.groupby('Месяц').agg({'amount': 'sum'}).rename(columns={'amount': 'Расход'}) if not df_expenses.empty else pd.DataFrame()
    
    # Итоговый DataFrame
    report = pd.concat([incomes_by_month, expenses_by_month], axis=1).fillna(0)
    report['Баланс'] = report['Доход'] - report['Расход']
    
    # Запись в Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        report.to_excel(writer, sheet_name='Отчет по месяцам')
        if not df_incomes.empty:
            df_incomes.to_excel(writer, sheet_name='Доходы', index=False)
        if not df_expenses.empty:
            df_expenses.to_excel(writer, sheet_name='Расходы', index=False)
    output.seek(0)
    return output
