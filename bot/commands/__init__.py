from .start import start
from .unknown_handler import unknown
from .help import help
from .vinylize import vinylize as vinylize_command
from bot.core import vinylizer
from .cancel import cancel
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from bot.states import *

def register_handlers(app: Application):
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)
    vinylize_handler = CommandHandler('vinylize', vinylize_command)

    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    app.add_handler(start_handler)
    app.add_handler(help_handler)
    # app.add_handler(MessageHandler(filters.AUDIO, configure))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('vinylize', vinylize_command)],
        states={
            CONFIGURE: [MessageHandler(filters.AUDIO, configure)],
            CONFIGURE_DECISION: [CallbackQueryHandler(configure_decision)],
            ALBUM: [CallbackQueryHandler(album)],
            RPM: [CallbackQueryHandler(rpm)],
            SAVE_IMAGE: [MessageHandler(filters.PHOTO, save_image)],
            NOISE: [CallbackQueryHandler(noise)],
            TIME: [CallbackQueryHandler(time_state)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    #app.add_handler(vinylize_handler)

    app.add_handler(conv_handler)

    # uknown command handler
    app.add_handler(unknown_handler)
    

