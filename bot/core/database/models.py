from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, MetaData
from typing import Optional
import datetime
from .database import engine, session
from bot.config import logger

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)
    time_created: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now())
    time_updated: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now(), 
                                                            onupdate=datetime.datetime.now())

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    premium: Mapped[Optional['Premium']] = relationship(back_populates='user', cascade='all, delete-orphan')

    @property
    def is_premium(self):
        return not self.check_if_premium_is_expired()
    
    def check_if_premium_is_expired(self):
        '''Checks if premium of the user is expired. If so, it removes it'''
        if self.premium is None:
            return True
        now = datetime.datetime.now()
        difference = now - self.premium.expire_date
        
        if difference.total_seconds() > 0:
            self.premium = None
            session.commit()
            return True
        return False

    def __repr__(self):
        return f'<User {self.telegram_id}>'

class Premium(Base):
    '''Contains data about premium, such as time it was expired, etc.'''
    __tablename__ = 'premiums'
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped['User'] = relationship(back_populates='premium', uselist=False)

    expire_date: Mapped[datetime.datetime]

    def __repr__(self):
        return f'<Premium {self.id}>'
    
Base.metadata.create_all(bind=engine)