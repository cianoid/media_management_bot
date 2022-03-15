from sqlalchemy import (BigInteger, Boolean, Column, create_engine, DateTime, ForeignKey,
                        Integer, String, SmallInteger)
from sqlalchemy.orm import declarative_base, relationship, validates
from sqlalchemy.sql import func

from app.core.constants import ALLOWED_TYPES

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger)
    registration_date = Column(
        DateTime(timezone=True), server_default=func.now())
    is_moderator = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    suggestions = relationship(
        'Suggestion', back_populates='user')

    def __repr__(self):
        return f'User(id={self.id!r}, name={self.chat_id!r})'


class Suggestion(Base):
    __tablename__ = 'suggestions'

    STATUS_NEW = 1
    STATUS_APPROVED = 2
    STATUS_REJECTED = 3

    STATUS_CHOICES = (STATUS_NEW, STATUS_APPROVED, STATUS_REJECTED)

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer, ForeignKey(f'{User.__tablename__}.id'), nullable=True)
    content_type = Column(String)
    content = Column(String)
    suggestion_date = Column(
        DateTime(timezone=True), server_default=func.now())

    status = Column(SmallInteger, default=STATUS_NEW)
    moderation_date = Column(DateTime(timezone=True))
    moderator_id = Column(
        Integer, ForeignKey(f'{User.__tablename__}.id'), nullable=True)

    @validates('content_type')
    def validate_content_type(self, key, value):
        if value not in ALLOWED_TYPES.keys():
            raise ValueError('{} not in list {}'.format(key, ALLOWED_TYPES))

    @validates('status')
    def validate_status(self, key, value):
        if value not in self.STATUS_CHOICES:
            raise ValueError(
                '{} not in list {}'.format(key, self.STATUS_CHOICES))


def db_init():
    engine = create_engine("sqlite:///db.db", echo=True, future=True)
    Base.metadata.create_all(engine)
