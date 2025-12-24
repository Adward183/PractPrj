import telebot
from handlers import commands, documents, messages
from config import BOT_TOKEN


def create_bot():

    bot = telebot.TeleBot(BOT_TOKEN)

    commands.register_handlers(bot)
    documents.register_handlers(bot)
    messages.register_handlers(bot)

    return bot


if __name__ == '__main__':
    print("Бот запущен")
    bot = create_bot()
    bot.polling(none_stop=True)