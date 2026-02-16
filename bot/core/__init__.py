from .vinylizer import Vinylizer
from .vinylizer_utils import v
from .vinylizer_queue import VinylizerQueue, RenderJob, get_locked_message
from .database import User, Premium
from bot.config import logger
from .database.utils import get_or_create_user

q = VinylizerQueue() # default queue
pq = VinylizerQueue() # premium queue

def get_queue(user_id: int) -> VinylizerQueue:
    user = get_or_create_user(user_id)
    if user is None:
        raise Exception('The user is None')
    if user.is_premium:
        return pq
    
    return q