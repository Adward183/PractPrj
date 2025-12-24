import pandas as pd
import re
import sys
from config import TOPIC_PATTERN, SCHEDULE_HEADERS, LESSONS_HEADERS, WEEK_DAYS


def check_dependencies():
    missing_deps = []

    try:
        import openpyxl
    except ImportError:
        missing_deps.append("openpyxl")

    try:
        import xlrd
    except ImportError:
        missing_deps.append("xlrd")

    if missing_deps:
        return False, missing_deps
    return True, []


def process_excel_file(file_path, filename):
    try:
        deps_ok, missing = check_dependencies()
        if not deps_ok:
            error_msg = (
                f"Отсутствуют необходимые библиотеки: {', '.join(missing)}\n\n"
                f"Установите их командой:\n"
                f"pip install {' '.join(missing)}"
            )
            return error_msg

        file_ext = filename.lower().split('.')[-1]

        if file_ext == 'xlsx':
            df = pd.read_excel(file_path, engine='openpyxl')
        elif file_ext == 'xls':
            df = pd.read_excel(file_path, engine='xlrd')
        else:
            return f"Неподдерживаемый формат файла: .{file_ext}\nОтправьте .xls или .xlsx файл"

        if is_schedule_file(df):
            return generate_schedule_report(df)
        elif is_lessons_file(df):
            return generate_lessons_report(df)
        else:
            return analyze_general_file(df, filename)

    except ImportError as e:
        return f"Ошибка импорта: {str(e)}\nУстановите необходимые библиотеки."

    except Exception as e:
        return f"Ошибка при чтении файла:\n{str(e)}"


def is_schedule_file(df):

    df_columns = [str(col).strip() for col in df.columns]

    schedule_keywords = ['группа', 'пара', 'время', 'понедельник', 'вторник', 'среда',
                         'четверг', 'пятница', 'суббота', 'воскресенье']

    found_keywords = 0
    for col in df_columns:
        col_lower = col.lower()
        for keyword in schedule_keywords:
            if keyword in col_lower:
                found_keywords += 1
                break

    return found_keywords >= 3


def is_lessons_file(df):

    df_columns = [str(col).strip() for col in df.columns]

    lessons_keywords = ['date', 'дата', 'лента', 'предмет', 'группа',
                        'фио преподавателя', 'преподаватель', 'тема урока', 'тема']

    found_keywords = 0
    for col in df_columns:
        col_lower = col.lower()
        for keyword in lessons_keywords:
            if keyword in col_lower:
                found_keywords += 1
                break

    return found_keywords >= 3


def generate_schedule_report(df, max_groups=20):
    try:
        group_col = find_column_by_keywords(df, ['группа'])
        subject_cols = find_day_columns(df)

        if not group_col:
            return "Не найден столбец с названием группы"

        if not subject_cols:
            return "Не найдены столбцы с дисциплинами по дням недели"

        groups = df[group_col].dropna().unique()

        display_groups = groups[:max_groups] if len(groups) > max_groups else groups

        report = "<b>ОТЧЕТ ПО РАСПИСАНИЮ НА НЕДЕЛЮ</b>\n\n"
        report += f"Всего групп в файле: <b>{len(groups)}</b>\n"

        if len(groups) > max_groups:
            report += f"<i>Показано первые {max_groups} групп</i>\n\n"
        else:
            report += "\n"

        for i, group in enumerate(display_groups, 1):
            group_data = df[df[group_col] == group]

            all_subjects = []
            for day_col in subject_cols:
                day_subjects = group_data[day_col].dropna()
                all_subjects.extend(day_subjects.tolist())

            if all_subjects:
                subject_counts = pd.Series(all_subjects).value_counts()

                report += f"<b>Группа: {group}</b>\n"
                report += f"Всего пар за неделю: <b>{len(all_subjects)}</b>\n\n"

                if len(subject_counts) > 0:
                    report += "<b>Количество пар по дисциплинам:</b>\n"

                    for subject, count in subject_counts.items():
                        if pd.notna(subject) and str(subject).strip():
                            report += f"{subject}: <b>{count}</b> пар\n"

                    report += "\n"
                else:
                    report += "Нет данных о дисциплинах\n\n"
            else:
                report += f"<b>Группа: {group}</b>\n"
                report += "Нет расписания для этой группы\n\n"

            if i < len(display_groups):
                report += "─" * 30 + "\n\n"

        if len(groups) > 1:
            report += "<b>ОБЩАЯ СТАТИСТИКА:</b>\n"

            all_file_subjects = []
            for day_col in subject_cols:
                day_subjects = df[day_col].dropna()
                all_file_subjects.extend(day_subjects.tolist())

            total_lessons = len([s for s in all_file_subjects if pd.notna(s) and str(s).strip()])
            unique_subjects = len(set([str(s).strip() for s in all_file_subjects if pd.notna(s) and str(s).strip()]))

            report += f"Всего пар в файле: <b>{total_lessons}</b>\n"
            report += f"Уникальных дисциплин: <b>{unique_subjects}</b>\n"

        return report

    except Exception as e:
        return f"Ошибка при анализе расписания:\n{str(e)}"


def generate_lessons_report(df, max_incorrect=30, max_correct=5):
    try:
        topic_col = find_column_by_keywords(df, ['тема урока', 'тема'])

        if topic_col is None:
            return "Не найден столбец с темами уроков"

        date_col = find_column_by_keywords(df, ['date', 'дата'])
        subject_col = find_column_by_keywords(df, ['предмет'])
        group_col = find_column_by_keywords(df, ['группа'])
        teacher_col = find_column_by_keywords(df, ['фио преподавателя', 'преподаватель'])

        correct = []
        incorrect = []
        incorrect_details = []

        for idx, row in df.iterrows():
            topic = row[topic_col] if topic_col in row and pd.notna(row[topic_col]) else ""
            topic_str = str(topic).strip()

            context = {
                'row': idx + 2,
                'date': str(row[date_col]) if date_col in row and pd.notna(row[date_col]) else "Нет данных",
                'subject': str(row[subject_col]) if subject_col in row and pd.notna(row[subject_col]) else "Нет данных",
                'group': str(row[group_col]) if group_col in row and pd.notna(row[group_col]) else "Нет данных",
                'teacher': str(row[teacher_col]) if teacher_col in row and pd.notna(row[teacher_col]) else "Нет данных",
                'topic': topic_str
            }

            if re.match(TOPIC_PATTERN, topic_str, re.IGNORECASE):
                correct.append(context)
            else:
                incorrect.append(context)
                incorrect_details.append(
                    f"Строка {context['row']}: {topic_str}"[:150]
                )

        report = "<b>ОТЧЕТ ПО ТЕМАМ УРОКОВ</b>\n\n"
        report += f"Всего записей: <b>{len(correct) + len(incorrect)}</b>\n"
        report += f"Корректных: <b>{len(correct)}</b>\n"
        report += f"Некорректных: <b>{len(incorrect)}</b>\n\n"

        if incorrect:
            report += f"<b>Некорректные записи (первые {min(max_incorrect, len(incorrect))}):</b>\n"

            for i, detail in enumerate(incorrect_details[:max_incorrect], 1):
                report += f"{i:2}. {detail}\n"

            if len(incorrect) > max_incorrect:
                report += f"\n<i>... и еще {len(incorrect) - max_incorrect} некорректных записей</i>\n"

            report += "\n<b>Примеры некорректных записей с деталями:</b>\n"
            for i, item in enumerate(incorrect[:3], 1):
                report += f"\n{i}. <b>Строка {item['row']}</b>\n"
                report += f"Дата: {item['date']}\n"
                report += f"Предмет: {item['subject']}\n"
                report += f"Группа: {item['group']}\n"
                report += f"Преподаватель: {item['teacher']}\n"
                report += f"Тема: <i>{item['topic']}</i>\n"

        if correct and len(incorrect) == 0:
            report += "\n<b>Все записи корректны!</b>\n"
        elif correct and len(incorrect) < 5:
            report += "\n<b>Примеры корректных записей:</b>\n"
            for i, item in enumerate(correct[:max_correct], 1):
                report += f"Строка {item['row']}: {item['topic']}\n"


        if incorrect:
            report += "\n<b>РЕКОМЕНДАЦИИ ПО ФОРМАТУ:</b>\n"
            report += "Правильный формат: <i>Урок № 1. Тема: Название темы</i>\n"
            report += "Примеры:\n"
            report += "Урок № 1. Тема: Введение в Python\n"
            report += "Урок № 2. Тема: Основы ООП\n"
            report += "Урок № 10. Тема: Работа с базами данных\n"
            report += "Введение в Python (без номера урока)\n"
            report += "Урок 1. Введение (без слова 'Тема:')\n"

        return report

    except Exception as e:
        return f"Ошибка при анализе тем уроков:\n{str(e)}"


def find_column_by_keywords(df, keywords):
    for col in df.columns:
        col_lower = str(col).lower()
        for keyword in keywords:
            if keyword in col_lower:
                return col
    return None


def find_day_columns(df):
    day_columns = []
    days_keywords = ['понедельник', 'вторник', 'среда', 'четверг',
                     'пятница', 'суббота', 'воскресенье']

    for col in df.columns:
        col_lower = str(col).lower()
        for day in days_keywords:
            if day in col_lower:
                day_columns.append(col)
                break

    return day_columns


def analyze_general_file(df, filename):

    report = f"<b>АНАЛИЗ ФАЙЛА: {filename}</b>\n\n"
    report += f"Столбцов: <b>{len(df.columns)}</b>\n"
    report += f"Строк: <b>{len(df)}</b>\n\n"

    report += "<b>Структура файла:</b>\n"
    for i, col in enumerate(df.columns, 1):
        non_null = df[col].count()
        percent = (non_null / len(df)) * 100 if len(df) > 0 else 0
        unique = df[col].nunique()

        report += f"{i:2}. <b>{col}</b>\n"
        report += f"Заполнено: {non_null}/{len(df)} ({percent:.1f}%)\n"
        report += f"Уникальных значений: {unique}\n"
        report += f"Тип данных: {df[col].dtype}\n"

        if non_null > 0:
            sample = df[col].dropna().iloc[0]
            sample_str = str(sample)
            if len(sample_str) > 50:
                sample_str = sample_str[:47] + "..."
            report += f"Пример: {sample_str}\n"

        report += "\n"

    if is_schedule_file(df):
        report += "<i>Похоже на файл расписания</i>\n"
    elif is_lessons_file(df):
        report += "<i>Похоже на файл тем уроков</i>\n"

    return report