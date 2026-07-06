
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db_connection import Database
from utils.formatting import POSITION_EMOJI, format_budget
from config import CURRENT_SEASON, BONUS_REWARDS
import csv
from datetime import datetime
from io import BytesIO
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_exports')
os.makedirs(EXPORTS_DIR, exist_ok=True)


async def show_export_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    telegram_id = user.id
    user_record = Database.execute_query(
        "SELECT id FROM users WHERE telegram_id = %s",
        params=(telegram_id,),
        fetch=True
    )

    if not user_record:
        await update.message.reply_text("❌ Ты не зарегистрирован. Напиши /start")
        return

    user_id = user_record[0]['id']
    team_record = Database.execute_query(
        "SELECT id, team_name FROM user_teams WHERE user_id = %s",
        params=(user_id,),
        fetch=True
    )

    if not team_record:
        await update.message.reply_text("❌ Команда не найдена")
        return
    keyboard = [
        [
            InlineKeyboardButton("📄 Экспорт в PDF", callback_data='export_pdf'),
            InlineKeyboardButton("📊 Экспорт в CSV", callback_data='export_csv'),
        ],
        [InlineKeyboardButton("❌ Отмена", callback_data='export_cancel')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📤 *Экспорт отчёта*\n\n"
        "Выбери формат файла:\n"
        "• 📄 **PDF** — красивый отчёт с составом и статистикой\n"
        "• 📊 **CSV** — таблица для Excel/Google Sheets",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def export_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    telegram_id = user.id
    data = query.data

    if data == 'export_cancel':
        await query.edit_message_text(" Экспорт отменён")
        return
    user_record = Database.execute_query(
        "SELECT id FROM users WHERE telegram_id = %s",
        params=(telegram_id,),
        fetch=True
    )
    if not user_record:
        await query.edit_message_text("❌ Пользователь не найден")
        return

    user_id = user_record[0]['id']

    if data == 'export_pdf':
        await query.edit_message_text("📄 Генерирую PDF отчёт...")
        filepath = _generate_pdf_report(user_id)

        if filepath and os.path.exists(filepath):
            with open(filepath, 'rb') as pdf_file:
                await query.message.reply_document(
                    document=pdf_file,
                    filename=os.path.basename(filepath),
                    caption="📄 Отчёт Fantasy Football"
                )
            await query.message.delete()
            try:
                os.remove(filepath)
            except:
                pass
        else:
            await query.edit_message_text("❌ Не удалось сгенерировать PDF")

    elif data == 'export_csv':
        await query.edit_message_text("📊 Генерирую CSV файл...")
        filepath = _generate_csv_report(user_id)

        if filepath and os.path.exists(filepath):
            with open(filepath, 'rb') as csv_file:
                await query.message.reply_document(
                    document=csv_file,
                    filename=os.path.basename(filepath),
                    caption="📊 Статистика в CSV формате"
                )
            await query.message.delete()
            try:
                os.remove(filepath)
            except:
                pass
        else:
            await query.edit_message_text("❌ Не удалось сгенерировать CSV")


def _get_cyrillic_font():

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    font_paths = [
        'C:/Windows/Fonts/arial.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
        'C:/Windows/Fonts/times.ttf',
        'C:/Windows/Fonts/timesbd.ttf',
        
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils', 'fonts', 'DejaVuSans.ttf'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils', 'fonts', 'DejaVuSans-Bold.ttf'),
    ]
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font_name = 'CyrillicFont'
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                return font_name
            except Exception as e:
                print(f"⚠️ Не удалось загрузить шрифт {font_path}: {e}")
                continue
    print("⚠️ Шрифт с кириллицей не найден! Использую Helvetica.")
    return 'Helvetica'


def _generate_pdf_report(user_id):

    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import mm
    font_name = _get_cyrillic_font()
    font_name_bold = font_name  # Для простоты используем тот же шрифт
    user = Database.execute_query(
        "SELECT first_name, budget, total_points FROM users WHERE id = %s",
        params=(user_id,),
        fetch=True
    )
    if not user:
        return None
    user = user[0]
    team = Database.execute_query(
        "SELECT team_name, formation, gameweek, season FROM user_teams WHERE user_id = %s",
        params=(user_id,),
        fetch=True
    )
    if not team:
        return None
    team = team[0]
    players = Database.execute_query(
        """
        SELECT 
            utp.is_captain,
            utp.is_vice_captain,
            utp.is_starting,
            utp.purchase_price,
            rp.name,
            rp.position,
            rp.total_points,
            rp.price,
            rt.short_name as team_name
        FROM user_team_players utp
        JOIN real_players rp ON utp.player_id = rp.id
        JOIN real_teams rt ON rp.current_team_id = rt.id
        WHERE utp.user_team_id = (SELECT id FROM user_teams WHERE user_id = %s)
        ORDER BY 
            CASE rp.position 
                WHEN 'GK' THEN 1 
                WHEN 'DF' THEN 2 
                WHEN 'MF' THEN 3 
                WHEN 'FW' THEN 4 
            END,
            utp.is_starting DESC
        """,
        params=(user_id,),
        fetch=True
    )
    filepath = os.path.join(EXPORTS_DIR, f'report_{user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    story = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name_bold,
        fontSize=20,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6*mm,
        alignment=1
    )
    story.append(Paragraph("Fantasy Football Report", title_style))
    story.append(Spacer(1, 5*mm))
    info_style = ParagraphStyle('Info', parent=styles['Normal'], fontName=font_name, fontSize=11)
    story.append(Paragraph(f"Менеджер: {user['first_name']}", info_style))
    story.append(Paragraph(f"Команда: {team['team_name']}", info_style))
    story.append(Paragraph(f"Схема: {team['formation']} | GW: {team['gameweek']} ({team['season']})", info_style))
    story.append(Paragraph(f"Бюджет: {float(user['budget']):.2f}M | Очки: {user['total_points']}", info_style))
    story.append(Spacer(1, 8*mm))
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], fontName=font_name_bold, fontSize=14, spaceAfter=4*mm)
    story.append(Paragraph("Состав команды", subtitle_style))
    table_data = [['Позиция', 'Игрок', 'Клуб', 'Цена', 'Очки', 'Роль']]

    for p in players:
        position = p['position']
        name = p['name']
        team_name = p['team_name']
        price = f"{p['price']}M"
        points = str(p['total_points'])

        role = ""
        if p['is_captain']:
            role = "Капитан"
        elif p['is_vice_captain']:
            role = "Вице"
        elif not p['is_starting']:
            role = "Скамейка"
        else:
            role = "Старт"

        table_data.append([position, name, team_name, price, points, role])
    col_widths = [20*mm, 45*mm, 25*mm, 20*mm, 20*mm, 35*mm]
    table = Table(table_data, colWidths=col_widths)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
        ('BACKGROUND', (0, 2), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(table)
    story.append(Spacer(1, 10*mm))
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontName=font_name, fontSize=8, textColor=colors.grey)
    story.append(Paragraph(f"Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}", footer_style))
    doc.build(story)

    return filepath


def _generate_csv_report(user_id):

    team = Database.execute_query(
        "SELECT team_name, gameweek, season FROM user_teams WHERE user_id = %s",
        params=(user_id,),
        fetch=True
    )
    if not team:
        return None
    team = team[0]
    players = Database.execute_query(
        """
        SELECT 
            rp.name,
            rp.position,
            rt.short_name as team_name,
            rp.price,
            rp.total_points,
            rp.form,
            utp.is_captain,
            utp.is_vice_captain,
            utp.is_starting,
            utp.purchase_price
        FROM user_team_players utp
        JOIN real_players rp ON utp.player_id = rp.id
        JOIN real_teams rt ON rp.current_team_id = rt.id
        WHERE utp.user_team_id = (SELECT id FROM user_teams WHERE user_id = %s)
        ORDER BY rp.total_points DESC
        """,
        params=(user_id,),
        fetch=True
    )

    if not players:
        return None
    filepath = os.path.join(EXPORTS_DIR, f'stats_{user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Fantasy Football Report'])
        writer.writerow([f"Команда: {team['team_name']}"])
        writer.writerow([f"Геймвик: {team['gameweek']} | Сезон: {team['season']}"])
        writer.writerow([f"Дата экспорта: {datetime.now().strftime('%d.%m.%Y %H:%M')}"])
        writer.writerow([])
        writer.writerow([
            'Позиция',
            'Игрок',
            'Клуб',
            'Текущая цена',
            'Цена покупки',
            'Всего очков',

            'Роль в команде'
        ])
        for p in players:
            role = ""
            if p['is_captain']:
                role = "Капитан"
            elif p['is_vice_captain']:
                role = "Вице-капитан"
            elif not p['is_starting']:
                role = "Скамейка"
            else:
                role = "Стартовый"

            writer.writerow([
                p['position'],
                p['name'],
                p['team_name'],
                f"{p['price']}M",
                f"{p['purchase_price']}M",
                p['total_points'],

                role
            ])

    return filepath