import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
from datetime import datetime

def generate_pdf_report(user_id: int, incomes: list, expenses: list) -> io.BytesIO:
    """
    Создаёт PDF-файл с таблицей доходов и расходов по категориям и дням.
    :param user_id: Telegram user id
    :param incomes: список доходов (dict с amount, category, created_at)
    :param expenses: список расходов (dict с amount, category, created_at)
    :return: BytesIO с PDF-файлом
    """
    # Готовим DataFrame для доходов и расходов
    df_incomes = pd.DataFrame(incomes)
    df_expenses = pd.DataFrame(expenses)

    # Группируем по дате и категории
    def group_by_day_and_category(df, value_col="amount"):
        if df.empty:
            return pd.DataFrame(columns=["Дата", "Категория", value_col])
        df["Дата"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d")
        grouped = df.groupby(["Дата", "category"])[value_col].sum().reset_index()
        return grouped

    income_table = group_by_day_and_category(df_incomes)
    expense_table = group_by_day_and_category(df_expenses)

    # Создаём PDF
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Заголовок
    elements.append(Paragraph("Отчёт по доходам и расходам по категориям и дням", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Доходы
    elements.append(Paragraph("Доходы", styles["Heading2"]))
    if not income_table.empty:
        data = [list(income_table.columns)] + income_table.values.tolist()
        table = Table(data, hAlign='LEFT')
        table.setStyle(TableStyle([
            # Стиль заголовка
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            # Стиль данных
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # белый фон
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),   # чёрный текст
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Нет данных по доходам", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Расходы
    elements.append(Paragraph("Расходы", styles["Heading2"]))
    if not expense_table.empty:
        data = [list(expense_table.columns)] + expense_table.values.tolist()
        table = Table(data, hAlign='LEFT')
        table.setStyle(TableStyle([
            # Стиль заголовка
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            # Стиль данных
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # белый фон
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),   # чёрный текст
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Нет данных по расходам", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Финализируем PDF
    doc.build(elements)
    output.seek(0)
    return output
