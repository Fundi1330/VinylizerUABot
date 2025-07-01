import logging
from telegram.ext import ApplicationBuilder
from os import environ
from bot.core import session, q
import asyncio

from bot import register_handlers, regitster_payment_handlers

def run_bot():
    application = ApplicationBuilder().token(environ.get('BOT_TOKEN')).build()

    register_handlers(application)
    regitster_payment_handlers(application)

    application.run_polling()

async def handle_teardown():
    await q.stop_worker()
    session.close()

if __name__ == '__main__':
    run_bot()
    asyncio.run(handle_teardown())