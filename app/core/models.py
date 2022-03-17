from datetime import datetime

from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        Integer, SmallInteger, String, create_engine, future,
                        select, update)
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import Session, declarative_base, relationship, validates
from sqlalchemy.sql import func

# from app.core.constants import ALLOWED_TYPES

Base = declarative_base()
SIZE = 10240


class User(Base):
    __tablename__ = 'users'

    tg_user_id = Column(BigInteger, unique=True, primary_key=True)
    tg_username = Column(String, nullable=True)
    registration_date = Column(
        DateTime(timezone=True), server_default=func.now())
    is_moderator = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        if self.tg_username:
            return f'@{self.tg_username} (id={self.tg_user_id!r})'

        return f'id={self.tg_user_id!r}'


class Suggestion(Base):
    __tablename__ = 'suggestions'

    STATUS_NEW = 1
    STATUS_APPROVED = 2
    STATUS_REJECTED = 3

    STATUS_CHOICES = (STATUS_NEW, STATUS_APPROVED, STATUS_REJECTED)

    pk = Column(Integer, primary_key=True)
    tg_user_id = Column(
        BigInteger, ForeignKey(f'{User.__tablename__}.tg_user_id'), nullable=True)
    tg_message_id = Column(BigInteger)

    content_type = Column(String, nullable=False)
    content_text = Column(String, nullable=True)
    content_file_id = Column(String, nullable=True)
    content_file_unique_id = Column(String, nullable=True)
    content_file_size = Column(BigInteger, nullable=True)
    content_file_name = Column(String, nullable=True)
    content_mime_type = Column(String, nullable=True)
    content_caption = Column(String, nullable=True)

    suggestion_date = Column(
        DateTime(timezone=True), server_default=func.now())
    status = Column(SmallInteger, default=STATUS_NEW)
    moderation_date = Column(DateTime(timezone=True))
    tg_moderator_id = Column(
        BigInteger,
        ForeignKey(f'{User.__tablename__}.tg_user_id'), nullable=True)

    user = relationship('User', foreign_keys=[tg_user_id], lazy='joined')
    moderator = relationship(
        'User', foreign_keys=[tg_moderator_id], lazy='joined')

    # @validates('content_type')
    # def validate_content_type(self, key, value):
    #     if value not in ALLOWED_TYPES.keys():
    #         raise ValueError('{} not in list {}'.format(key, ALLOWED_TYPES))

    # @validates('status')
    # def validate_status(self, key, value):
    #     if value not in self.STATUS_CHOICES:
    #         raise ValueError(
    #             '{} not in list {}'.format(key, self.STATUS_CHOICES))


class __DBLayer:
    model: Base
    engine: future.Engine

    def __init__(self):
        self.engine = create_engine("sqlite:///db.db", echo=False, future=True)
        Base.metadata.create_all(self.engine)


class DBUser(__DBLayer):
    model = User

    def get(self, tg_user_id):
        session = Session(self.engine)
        stmt = select(User).where(User.tg_user_id == tg_user_id)

        return session.scalar(stmt)

    def create(self, tg_user_id, tg_username):
        with Session(self.engine) as session:
            session.add(User(tg_user_id=tg_user_id, tg_username=tg_username))
            session.commit()

    def get_or_create(self, tg_user_id, tg_username):
        obj = self.get(tg_user_id=tg_user_id)

        if obj:
            return obj

        self.create(tg_user_id=tg_user_id, tg_username=tg_username)

        return self.get(tg_user_id=tg_user_id)

    def get_user_id(self, tg_user_id):
        obj = self.get(tg_user_id=tg_user_id)

        if not obj:
            return None

        return obj.pk

    def get_moderator_list(self):
        session = Session(self.engine)
        stmt = select(User).where(
            User.is_moderator.is_(True), User.is_active.is_(True))

        return session.scalars(stmt).all()

    def get_moderator_ids(self):
        return [user.tg_user_id for user in self.get_moderator_list()]

    def update(self, tg_user_id, update_data):
        with Session(self.engine) as session:
            try:
                obj = session.query(self.model).get(tg_user_id)

                for key, value in update_data.items():
                    setattr(obj, key, value)

                session.commit()
                session.flush()

                return True
            except StatementError:
                return False


class DBSuggestion(__DBLayer):
    model = Suggestion

    def create(self, tg_user_id, **kwargs):
        with Session(self.engine) as session:
            obj = Suggestion(tg_user_id=tg_user_id, **kwargs)

            session.add(obj)
            session.commit()

            return obj.pk

    def get(self, pk):
        session = Session(self.engine)
        stmt = select(self.model).where(getattr(self.model, 'pk') == pk)

        return session.scalar(stmt)

    def get_new_suggestion_list(self):
        session = Session(self.engine)
        stmt = select(Suggestion).where(
            Suggestion.status==Suggestion.STATUS_NEW)

        return session.scalars(stmt).all()

    def update(self, pk, update_data):
        with Session(self.engine) as session:
            try:
                obj = session.query(Suggestion).get(pk)

                for key, value in update_data.items():
                    setattr(obj, key, value)

                session.commit()
                session.flush()

                return True
            except StatementError:
                return False
