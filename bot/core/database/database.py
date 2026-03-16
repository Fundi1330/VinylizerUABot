from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from bot.config import config

engine = create_engine(f"sqlite://{config.database_path}")

Sess = sessionmaker(bind=engine)

def get_session() -> Session:
    with Sess() as sess:
        return sess