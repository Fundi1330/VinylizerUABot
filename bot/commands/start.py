from telegram import Update
from telegram.ext import ContextTypes
from bot.core import session, User

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '''
Вітаю👋! Я - бот-вінілізатор.
Надішліть мені аудіо і я перетворю його у кружечок з вініловою пластинкою.
Напишіть /vinylize, щоб розпочати.
    '''
    usr_id = update.effective_user.id
    user = session.query(User).filter_by(telegram_id=usr_id).one_or_none()
    if user is None:
        user = User(telegram_id=usr_id)

        session.add(user)
        session.commit()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)