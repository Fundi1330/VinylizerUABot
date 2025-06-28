from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from bot.config import config

engine = create_engine(f'sqlite://{config.get('database_path')}')

Session = sessionmaker(bind=engine)
session = Session()