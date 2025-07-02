from .precheckout import precheckout_callback
from .successful import successful_payment_callback
from telegram.ext import filters, Application, PreCheckoutQueryHandler, MessageHandler

def register_payment_handlers(app: Application):
    precheckout_handler = PreCheckoutQueryHandler(precheckout_callback)
    successful_payment_handler = MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)

    app.add_handler(precheckout_handler)
    app.add_handler(successful_payment_handler)