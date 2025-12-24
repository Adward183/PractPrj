import webbrowser
import telebot
from utils.helpers import show_help

def register_handlers(bot):

    @bot.message_handler(commands=['start'])
    def start(message):
        welcome_text = (f"Привет, <b>{message.from_user.first_name}</b>!"
                        f"\nИспользуйте /help для дополнительной информации.")

        bot.send_message(message.chat.id, welcome_text, parse_mode='html')

    @bot.message_handler(commands=['help'])
    def help_command(message):
        show_help(bot, message.chat.id)