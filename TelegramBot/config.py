import os
import sys

BOT_TOKEN = os.getenv('BOT_TOKEN', '8493080910:AAE-LWsPVF8LYoO_ptLB4yMdL_q3P1r5NNo')

if not BOT_TOKEN:
    print("ОШИБКА: Токен бота не найден!")
    sys.exit(1)

ALLOWED_MIME_TYPES = [
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
]

TOPIC_PATTERN = r'^Урок\s*№?\s*\d+\.?\s*Тема:\s*.+$'


SCHEDULE_HEADERS = [
    'Группа', 'Пара', 'Время', 'Понедельник', 'Вторник', 'Среда',
    'Четверг', 'Пятница', 'Суббота', 'Воскресенье'
]

LESSONS_HEADERS = [
    'Date', 'Лента', 'Предмет', 'Группа', 'ФИО преподавателя', 'Тема урока'
]

WEEK_DAYS = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']