import json

from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        Integer, SmallInteger, String, Text,
                        create_engine, future, select)
from sqlalchemy.orm import Session, declarative_base, relationship, validates
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator

from app.core.constants import ALLOWED_TYPES

Base = declarative_base()
SIZE = 10240


class DictType(TypeDecorator):
    impl = Text(SIZE)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class User(Base):
    __tablename__ = 'users'

    tg_user_id = Column(BigInteger, unique=True, primary_key=True)
    registration_date = Column(
        DateTime(timezone=True), server_default=func.now())
    is_moderator = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f'User(id={self.id!r}, name={self.tg_user_id!r})'


class Suggestion(Base):
    __tablename__ = 'suggestions'

    STATUS_NEW = 1
    STATUS_APPROVED = 2
    STATUS_REJECTED = 3

    STATUS_CHOICES = (STATUS_NEW, STATUS_APPROVED, STATUS_REJECTED)

    id = Column(Integer, primary_key=True)

    tg_user_id = Column(
        Integer, ForeignKey(f'{User.__tablename__}.tg_user_id'), nullable=True)
    content_type = Column(String)
    content = Column(DictType)
    suggestion_date = Column(
        DateTime(timezone=True), server_default=func.now())
    status = Column(SmallInteger, default=STATUS_NEW)
    moderation_date = Column(DateTime(timezone=True))
    moderator_id = Column(
        Integer, ForeignKey(f'{User.__tablename__}.tg_user_id'), nullable=True)

    user = relationship('User', foreign_keys=[tg_user_id])
    moderator = relationship('User', foreign_keys=[moderator_id])

    # @validates('content_type')
    # def validate_content_type(self, key, value):
    #     if value not in ALLOWED_TYPES.keys():
    #         raise ValueError('{} not in list {}'.format(key, ALLOWED_TYPES))

    @validates('status')
    def validate_status(self, key, value):
        if value not in self.STATUS_CHOICES:
            raise ValueError(
                '{} not in list {}'.format(key, self.STATUS_CHOICES))


class __DBLayer:
    engine: future.Engine

    def __init__(self):
        self.engine = create_engine("sqlite:///db.db", echo=False, future=True)
        Base.metadata.create_all(self.engine)


class DBUser(__DBLayer):
    def get(self, tg_user_id):
        stmt = select(User).where(User.tg_user_id == tg_user_id)

        with Session(self.engine) as session:
            return session.scalar(stmt)

    def create(self, tg_user_id):
        with Session(self.engine) as session:
            session.add(User(tg_user_id=tg_user_id))
            session.commit()

    def get_or_create(self, tg_user_id):
        obj = self.get(tg_user_id=tg_user_id)

        if obj:
            return obj

        self.create(tg_user_id=tg_user_id)
        return self.get(tg_user_id=tg_user_id)

    def get_user_id(self, tg_user_id):
        obj = self.get(tg_user_id=tg_user_id)

        if not obj:
            return None

        return obj.id

    def get_moderator_ids(self):
        stmt = select(User).where(
            User.is_moderator.is_(True), User.is_active.is_(True))

        with Session(self.engine) as session:
            return [user.tg_user_id for user in session.scalars(stmt)]


class DBSuggestion(__DBLayer):
    def create(self, tg_user_id, content_type, content):
        with Session(self.engine) as session:
            session.add(Suggestion(
                tg_user_id=tg_user_id, content_type=content_type,
                content=content))
            session.commit()

