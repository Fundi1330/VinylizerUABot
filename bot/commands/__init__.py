from .start import start_command
from .unknown_handler import unknown
from .help import help_command
from .vinylize import vinylize_command
from .premium import premium_command
from .cancel import cancel_command
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from bot.states import *

def register_handlers(app: Application):
    start_handler = CommandHandler('start', start_command)
    help_handler = CommandHandler('help', help_command)
    premium_handler = CommandHandler('premium', premium_command)

    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    app.add_handler(start_handler)
    app.add_handler(help_handler)
    app.add_handler(premium_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('vinylize', vinylize_command)],
        states={
            CONFIGURE: [
                MessageHandler(filters.AUDIO, file_download_callback, block=False), 
                MessageHandler(filters.VIDEO, file_download_callback, block=False),
                MessageHandler(filters.TEXT & (filters.Regex(r'^https://www\.youtube\.com') |
                                               filters.Regex(r'^https://www\.youtu\.be') |
                                               filters.Regex(r'^https://youtube\.com') |
                                               filters.Regex(r'^https://youtu\.be')
                                              ), file_download_callback, block=False)],
            CONFIGURE_DECISION: [CallbackQueryHandler(decision_callback)],
            SELECT_VINYL: [CallbackQueryHandler(select_vinyl_callback)],
            ALBUM: [CallbackQueryHandler(album_callback)],
            RPM: [CallbackQueryHandler(rpm_callback)],
            SAVE_IMAGE: [MessageHandler(filters.PHOTO, save_image_callback)],
            NOISE: [CallbackQueryHandler(noise_callback)],
            MANUAL_TIME_CHOICE: [
                MessageHandler(filters.TEXT & (filters.Regex(r'(?<!\d:)(?<!\d)[0-5]?\d:[0-5]?\d:[0-5]\d(?!:?\d)') |
                                               filters.Regex(r'(?<!\d:)(?<!\d)[0-5]?\d:[0-5]\d(?!:?\d)') |
                                               filters.Regex(r'(?<!\d:)(?<!\d)[0-5]\d(?!:?\d)') 
                                               ), manual_time_choice_callback)
            ],
            TIME: [CallbackQueryHandler(time_state_callback)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)

    # uknown command handler
    app.add_handler(unknown_handler)
    

