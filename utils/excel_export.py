import io
import pandas as pd
from datetime import datetime
from xlsxwriter.utility import xl_rowcol_to_cell

async def generate_excel_report(user_id: int, incomes: list, expenses: list) -> io.BytesIO:
    """
    Создает Excel-файл с доходами и расходами пользователя по дням и категориям.
    :param user_id: Telegram user id
    :param incomes: список доходов (dict с amount, category, created_at)
    :param expenses: список расходов (dict с amount, category, created_at)
    :return: BytesIO с Excel-файлом
    """
    # Преобразуем данные в DataFrame
    df_incomes = pd.DataFrame(incomes) if incomes else pd.DataFrame()
    df_expenses = pd.DataFrame(expenses) if expenses else pd.DataFrame()
    
    # Функция для группировки по дате и категории
    def group_by_day_and_category(df, value_col="amount"):
        if df.empty:
            return pd.DataFrame(columns=["Дата", "Категория", value_col])
        df["Дата"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d")
        grouped = df.groupby(["Дата", "category"])[value_col].sum().reset_index()
        return grouped
    
    # Группировка по дням и категориям
    income_table = group_by_day_and_category(df_incomes)
    expense_table = group_by_day_and_category(df_expenses)
    
    # Добавим также группировку по месяцам для сводной информации
    if not df_incomes.empty:
        df_incomes['Месяц'] = pd.to_datetime(df_incomes['created_at']).dt.to_period('M')
    if not df_expenses.empty:
        df_expenses['Месяц'] = pd.to_datetime(df_expenses['created_at']).dt.to_period('M')
    
    # Группировка по месяцам
    incomes_by_month = df_incomes.groupby('Месяц').agg({'amount': 'sum'}).rename(columns={'amount': 'Доход'}) if not df_incomes.empty else pd.DataFrame()
    expenses_by_month = df_expenses.groupby('Месяц').agg({'amount': 'sum'}).rename(columns={'amount': 'Расход'}) if not df_expenses.empty else pd.DataFrame()
    
    # Итоговый DataFrame для месячной сводки
    monthly_report = pd.concat([incomes_by_month, expenses_by_month], axis=1).fillna(0)
    monthly_report['Баланс'] = monthly_report['Доход'] - monthly_report['Расход']
    
    # Запись в Excel с улучшенным форматированием
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Лист 1: Сводка по месяцам
        monthly_report.to_excel(writer, sheet_name='Сводка по месяцам')
        
        # Получаем рабочий лист для форматирования
        workbook = writer.book
        worksheet = writer.sheets['Сводка по месяцам']
        
        # Определяем форматы
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#4B88CB',
            'font_color': 'white',
            'border': 1
        })
        
        income_format = workbook.add_format({
            'num_format': '#,##0.00',
            'align': 'right',
            'fg_color': '#E6F2FF'
        })
        
        expense_format = workbook.add_format({
            'num_format': '#,##0.00',
            'align': 'right',
            'fg_color': '#FFECEC'
        })
        
        balance_format = workbook.add_format({
            'num_format': '#,##0.00',
            'align': 'right',
            'bold': True
        })
        
        # Применяем форматирование к заголовкам
        for col_num, value in enumerate(['', 'Месяц', 'Доход', 'Расход', 'Баланс']):
            worksheet.write(0, col_num, value, header_format)
        
        # Устанавливаем ширину столбцов
        worksheet.set_column('A:A', 5)  # Столбец с индексом
        worksheet.set_column('B:B', 15) # Столбец с месяцем
        worksheet.set_column('C:E', 12) # Столбцы с суммами
        
        # Лист 2: Доходы по дням и категориям
        if not income_table.empty:
            income_table.to_excel(writer, sheet_name='Доходы по дням', index=False)
            worksheet_income = writer.sheets['Доходы по дням']
            
            # Форматируем заголовки
            for col_num, value in enumerate(['Дата', 'Категория', 'amount']):
                worksheet_income.write(0, col_num, value, header_format)
                
            # Форматируем данные
            for row_num in range(1, len(income_table) + 1):
                worksheet_income.write_string(row_num, 0, str(income_table.iloc[row_num-1]['Дата']))
                worksheet_income.write_string(row_num, 1, str(income_table.iloc[row_num-1]['category']))
                worksheet_income.write_number(row_num, 2, float(income_table.iloc[row_num-1]['amount']), income_format)
                
            worksheet_income.set_column('A:A', 15)  # Дата
            worksheet_income.set_column('B:B', 20)  # Категория
            worksheet_income.set_column('C:C', 12)  # Сумма
        
        # Лист 3: Расходы по дням и категориям
        if not expense_table.empty:
            expense_table.to_excel(writer, sheet_name='Расходы по дням', index=False)
            worksheet_expense = writer.sheets['Расходы по дням']
            
            # Форматируем заголовки
            for col_num, value in enumerate(['Дата', 'Категория', 'amount']):
                worksheet_expense.write(0, col_num, value, header_format)
                
            # Форматируем данные
            for row_num in range(1, len(expense_table) + 1):
                worksheet_expense.write_string(row_num, 0, str(expense_table.iloc[row_num-1]['Дата']))
                worksheet_expense.write_string(row_num, 1, str(expense_table.iloc[row_num-1]['category']))
                worksheet_expense.write_number(row_num, 2, float(expense_table.iloc[row_num-1]['amount']), expense_format)
                
            worksheet_expense.set_column('A:A', 15)  # Дата
            worksheet_expense.set_column('B:B', 20)  # Категория
            worksheet_expense.set_column('C:C', 12)  # Сумма
            
        # Лист 4: Детальные данные (если нужны)
        if not df_incomes.empty:
            df_incomes.to_excel(writer, sheet_name='Детальные доходы', index=False)
        if not df_expenses.empty:
            df_expenses.to_excel(writer, sheet_name='Детальные расходы', index=False)
    
    output.seek(0)
    return output
