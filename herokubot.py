import logging
import os
import corina_api
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

faq_examples = ["Was ist Corona?",
                "Wie stecke ich mich an?",
                "Wo kann ich mich testen lassen?",
                "Was kostet ein Test?",
                "Was soll ich tun?",
                "Kann man sich impfen lassen?",
                "Wie wäscht man sich die Hände?",
                "Was mache ich wenn ich ein Verdachtsfall bin?",
                "Gibt es eine Behandlung?",
                "Wo kann ich noch einkaufen?",
                "FAQ beenden"]


# Einfacher Start-Befehl. Zeigt den Text unter /start an.
def start(bot, update):
    text = "Hallo"
    response, image = corina_api.question(text, update.effective_chat.id)
    if image:
        update.effective_message.reply_photo(image, caption=response)
    else:
        update.effective_message.reply_text(response)


# Wenn der Befehl /faq ausgeführt wird, wird eine Reihe an Knöpfen mit häufig gestellten Fragen angezeigt
def faq(bot, update):
    keyboard = []
    for q in faq_examples:
        keyboard.append([KeyboardButton(q)])
    text = "Hier findest du ein paar häufig gestellte Fragen zum Coronavirus, die ich dir gerne beantworte. " \
           "Drücke einfach /endfaq wenn du fertig bist."
    update.effective_message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard))


def endfaq(bot, update):
    text = "Das FAQ wurde beendet."
    update.effective_message.reply_text(text, reply_markup=ReplyKeyboardRemove())


def answer(bot, update, text):
    response, image, options = corina_api.question(text, update.effective_chat.id)
    keyboard = None
    if options:
        k = []
        for o in options:
            k.append([InlineKeyboardButton(o[0], callback_data=o[1])])
        keyboard = InlineKeyboardMarkup(k)
    if image:
        update.effective_message.reply_photo(image, caption=response, reply_markup=keyboard, parse_mode="HTML")
    else:
        update.effective_message.reply_text(response, reply_markup=keyboard, parse_mode='HTML')


def answer_text(bot, update):
    text = update.effective_message.text
    answer(bot, update, text)


def answer_callback(bot, update):
    text = update.callback_query.data
    answer(bot, update, text)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


if __name__ == "__main__":
    # Set these variable to the appropriate values
    TOKEN = os.getenv("TOKEN")
    NAME = os.getenv("NAME")

    # Port is given by Heroku
    PORT = os.environ.get('PORT')

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    # Add handlers
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('faq', faq))
    dp.add_handler(CommandHandler('endfaq', endfaq))
    dp.add_handler(MessageHandler(Filters.text and Filters.regex('^FAQ beenden$'), endfaq))
    dp.add_handler(MessageHandler(Filters.text, answer_text))
    dp.add_handler(CallbackQueryHandler(answer_callback))
    dp.add_error_handler(error)

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
    updater.idle()
