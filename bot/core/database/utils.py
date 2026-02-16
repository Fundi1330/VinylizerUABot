from . import User, get_session

def get_or_create_user(telegram_id: int) -> User:
    session = get_session()
    user = session.query(User).filter_by(telegram_id=telegram_id).one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id)
        session.add(user)
        session.commit()
    return user