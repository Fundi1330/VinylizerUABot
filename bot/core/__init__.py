from .vinylizer import Vinylizer
from .vinylizer_utils import v
from .vinylizer_queue import VinylizerQueue, get_locked_message
from .database import session, User, Premium
from bot.config import logger

q = VinylizerQueue() # default queue
pq = VinylizerQueue() # premium queue

def get_queue(user_id: int) -> VinylizerQueue:
    user = session.query(User).filter_by(telegram_id=user_id).one_or_none()
    if user is None:
        raise Exception('The user is None')
    if user.is_premium:
        logger.info('Using PremiumQueue')
        return pq
    
    return q

