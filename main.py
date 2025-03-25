import logging
from telegram.ext import ApplicationBuilder
from os import environ

from bot import register_handlers

def run_bot():
    application = ApplicationBuilder().token(environ.get('BOT_TOKEN')).build()

    register_handlers(application)

    application.run_polling()

if __name__ == '__main__':
    run_bot()