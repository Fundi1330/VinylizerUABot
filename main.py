import logging
from telegram.ext import ApplicationBuilder
from os import environ
from bot.core import session, q, pq
import asyncio

from bot import register_handlers, register_payment_handlers

def run_bot():
    # application = ApplicationBuilder().base_url('https://api.telegram.org/bot{token}/test').token(environ.get('BOT_TOKEN')).build() # test backend
    application = ApplicationBuilder().token(environ.get('BOT_TOKEN')).build()
    register_handlers(application)
    register_payment_handlers(application)

    application.run_polling()

async def handle_teardown():
    await q.stop_worker()
    await pq.stop_worker()
    session.close()

if __name__ == '__main__':
    run_bot()
    asyncio.run(handle_teardown())