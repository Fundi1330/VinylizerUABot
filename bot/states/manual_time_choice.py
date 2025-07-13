from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from .state_utils import create_queue_task
from telegram.ext import ConversationHandler

MANUAL_TIME_CHOICE = 7

async def manual_time_choice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Handles the user-inputed timecode'''
    text = '''
    ✅Час початку успішно встановленно вручну!
    '''
    try:
        timecode_parts = update.effective_message.text.split(':')
        if len(timecode_parts) > 2:
            timecode_datetime = datetime.strptime(update.effective_message.text, '%H:%M:%S')
        elif len(timecode_parts) > 1:
            timecode_datetime = datetime.strptime(update.effective_message.text, '%M:%S')
        else:
            timecode_datetime = datetime.strptime(update.effective_message.text, '%S')
        start_time = timedelta(hours=timecode_datetime.hour, minutes=timecode_datetime.minute, seconds=timecode_datetime.second)
        start_time = start_time.total_seconds()
        if start_time > context.user_data.get('audio_duration'):
            text = '''❌Ваш таймкод не відповідає довжині відео. Спробуйте ще раз!'''
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                                        text=text)
            return MANUAL_TIME_CHOICE    
        context.user_data['start_time'] = start_time
    except ValueError:
        text = '''❌Ви ввели таймкод у неправильному форматі. Спробуйте ще раз!'''
        await context.bot.send_message(chat_id=update.effective_chat.id, 
                                       text=text)
        return MANUAL_TIME_CHOICE    

    await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=context.user_data.get('message_id'),
                                    text=text)
    context.user_data['message_id'] = None
    await create_queue_task(update, context)

    return ConversationHandler.END