import telebot
import tempfile
import os
import math


def show_help(bot, chat_id):
    help_text = """

<b>РАБОТА С ФАЙЛАМИ:</b>

<b>1.Расписание групп (на неделю)</b>
• Столбцы: Группа, Пара, Время, Понедельник, Вторник...
• В ячейках дней: названия дисциплин
• Результат: количество пар по каждой дисциплине

<b>2.Темы уроков</b>
Столбцы: Date, Лента, Предмет, Группа, ФИО преподавателя, Тема урока
Формат тем: "Урок № _. Тема: _"
Результат: проверка формата, список некорректных

<b>ПОДСКАЗКИ:</b>
Файлы могут быть .xls или .xlsx

"""
    bot.send_message(chat_id, help_text, parse_mode='html')


def send_as_file(bot, chat_id, text, filename="report.txt", caption="Отчет"):
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                     suffix='.txt', delete=False) as f:
        f.write(text)
        temp_path = f.name

    try:
        with open(temp_path, 'rb') as file:
            bot.send_document(chat_id, file, caption=caption, visible_file_name=filename)
    finally:
        os.unlink(temp_path)


def smart_send(bot, chat_id, text, parse_mode='html'):

    MAX_MESSAGE_LENGTH = 4000

    if len(text) > MAX_MESSAGE_LENGTH:
        if 'ОТЧЕТ ПО РАСПИСАНИЮ' in text:
            filename = "расписание_групп.txt"
            caption = "Отчет по расписанию групп"
        elif 'ОТЧЕТ ПО ТЕМАМ УРОКОВ' in text:
            filename = "темы_уроков.txt"
            caption = "Отчет по темам уроков"
        else:
            filename = "анализ_файла.txt"
            caption = "Анализ файла"

        send_as_file(bot, chat_id, text, filename, caption)

        if 'ОТЧЕТ ПО РАСПИСАНИЮ' in text:
            summary = "<b>Отчет по расписанию готов!</b>\n"
            summary += "Я отправил подробный отчет файлом.\n"
            summary += "Проверьте количество пар по каждой дисциплине."
        elif 'ОТЧЕТ ПО ТЕМАМ УРОКОВ' in text:
            summary = "<b>Отчет по темам уроков готов!</b>\n"
            summary += "Я отправил подробный отчет файлом.\n"
            summary += "Проверьте корректность форматов тем."
        else:
            summary = "<b>Анализ файла завершен!</b>\n"
            summary += "Я отправил подробный отчет файлом."

        bot.send_message(chat_id, summary, parse_mode='html')
    else:
        bot.send_message(chat_id, text, parse_mode=parse_mode)