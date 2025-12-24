import telebot
import os
from config import ALLOWED_MIME_TYPES
from utils.excel_processor import process_excel_file


def register_handlers(bot):
    @bot.message_handler(content_types=['document'])
    def handle_document(message):
        if message.document.mime_type in ALLOWED_MIME_TYPES:
            try:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)

                filename = message.document.file_name
                temp_path = f"temp_{message.chat.id}_{filename}"

                with open(temp_path, 'wb') as new_file:
                    new_file.write(downloaded_file)

                response = process_excel_file(temp_path, filename)

                bot.send_message(message.chat.id, response, parse_mode='html')

            except Exception as e:
                error_msg = f"Ошибка при обработке файла:\n{str(e)}"
                bot.send_message(message.chat.id, error_msg)

            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        else:
            bot.send_message(message.chat.id, "Пожалуйста, отправьте файл в формате .xls или .xlsx")