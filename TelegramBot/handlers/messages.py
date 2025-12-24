import telebot

def register_handlers(bot):
    @bot.message_handler(func=lambda message: True)
    def handle_messages(message):
        text = message.text.lower()

        if text == 'привет':
            bot.send_message(message.chat.id,
                             f'Привет, <b>{message.from_user.first_name}</b>!',
                             parse_mode='html')
        elif text == 'id':
            bot.reply_to(message, f'Ваш ID: {message.from_user.id}')


        elif text in ['расписание', 'темы', 'отчет']:
            help_text = {
                'расписание': 'Для отчета по расписанию отправьте Excel-файл с колонкой "Предмет" или "Дисциплина"',
                'темы': 'Для проверки тем отправьте Excel-файл с колонкой "Тема" в формате "Урок № _. Тема: _"',
                'отчет': 'Отправьте Excel-файл для анализа. Я определю тип отчета автоматически.'
            }
            bot.send_message(message.chat.id, help_text[text])

        else:

            pass