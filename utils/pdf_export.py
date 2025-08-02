import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
from datetime import datetime

# Используем стандартные шрифты ReportLab, которые всегда доступны
# В ReportLab есть встроенные шрифты: Helvetica, Helvetica-Bold, Courier, Times-Roman и т.д.

def generate_pdf_report(user_id: int, incomes: list, expenses: list) -> io.BytesIO:
    """
    Создаёт PDF-файл с таблицей доходов и расходов по категориям и дням.
    :param user_id: Telegram user id
    :param incomes: список доходов (dict с amount, category, created_at)
    :param expenses: список расходов (dict с amount, category, created_at)
    :return: BytesIO с PDF-файлом
    """
    try:
        # Готовим DataFrame для доходов и расходов
        df_incomes = pd.DataFrame(incomes) if incomes else pd.DataFrame()
        df_expenses = pd.DataFrame(expenses) if expenses else pd.DataFrame()
        
        # Группируем по дате и категории
        def group_by_day_and_category(df, value_col="amount"):
            if df.empty:
                return pd.DataFrame(columns=["Дата", "Категория", value_col])
            df["Дата"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d")
            grouped = df.groupby(["Дата", "category"])[value_col].sum().reset_index()
            return grouped

        income_table = group_by_day_and_category(df_incomes)
        expense_table = group_by_day_and_category(df_expenses)

        # Создаём PDF в простой текстовой форме (без сложных стилей)
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        elements = []
        
        # Используем встроенный стиль и создаем свой для заголовков
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.black,
            alignment=1,  # центрирование
            spaceAfter=12
        )
        
        # Стиль для подзаголовков
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=colors.black,
            alignment=1,
            spaceAfter=8
        )
        
        # Заголовок
        elements.append(Paragraph("Отчёт по доходам и расходам по категориям и дням", title_style))
        elements.append(Spacer(1, 20))

        # === ДОХОДЫ - формируем простую таблицу без сложного форматирования ===
        elements.append(Paragraph("ДОХОДЫ", heading_style))
        elements.append(Spacer(1, 10))
        
        if not income_table.empty:
            # Преобразуем данные в строки текста
            income_data = [["Дата", "Категория", "Сумма"]]
            
            for _, row in income_table.iterrows():
                income_data.append([row['Дата'], str(row['category']), f"{float(row['amount']):.2f}"])
                
            # Создаем простую таблицу
            income_tbl = Table(income_data, colWidths=[100, 150, 100])
            income_tbl.setStyle(TableStyle([
                # Основные рамки
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                # Заголовок - белый текст на синем фоне
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                # Данные - простой черный текст на белом фоне
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                # Выравнивание и шрифты
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),  # заголовок
                ('FONTSIZE', (0, 1), (-1, -1), 10),  # данные
            ]))
            elements.append(income_tbl)
        else:
            p = Paragraph("Нет данных по доходам", styles["Normal"])
            p.style.textColor = colors.black
            elements.append(p)
            
        elements.append(Spacer(1, 20))
        
        # === РАСХОДЫ - формируем простую таблицу без сложного форматирования ===
        elements.append(Paragraph("РАСХОДЫ", heading_style))
        elements.append(Spacer(1, 10))
        
        if not expense_table.empty:
            # Преобразуем данные в строки текста
            expense_data = [["Дата", "Категория", "Сумма"]]
            
            for _, row in expense_table.iterrows():
                expense_data.append([row['Дата'], str(row['category']), f"{float(row['amount']):.2f}"])
                
            # Создаем простую таблицу
            expense_tbl = Table(expense_data, colWidths=[100, 150, 100])
            expense_tbl.setStyle(TableStyle([
                # Основные рамки
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                # Заголовок - белый текст на красном фоне
                ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                # Данные - простой черный текст на белом фоне
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                # Выравнивание и шрифты
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),  # заголовок
                ('FONTSIZE', (0, 1), (-1, -1), 10),  # данные
            ]))
            elements.append(expense_tbl)
        else:
            p = Paragraph("Нет данных по расходам", styles["Normal"])
            p.style.textColor = colors.black
            elements.append(p)
            
        elements.append(Spacer(1, 12))
        
        # Завершаем построение документа
        doc.build(elements)
        output.seek(0)
        return output
        
    except Exception as e:
        # В случае ошибки создаем простой PDF с сообщением об ошибке
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Произошла ошибка при создании отчета: {str(e)}", styles["Title"]))
        doc.build(elements)
        output.seek(0)
        return output
