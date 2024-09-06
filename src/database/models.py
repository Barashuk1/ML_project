from sqlalchemy.orm import (
    Mapped, mapped_column, relationship, declarative_base
)
from sqlalchemy import String, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String(256))
    email: Mapped[str] = mapped_column(String(256))
    password: Mapped[str] = mapped_column(String(256))
    chats: Mapped['Chat'] = relationship('Chat', backref='user')
    history: Mapped['History'] = relationship('History', backref='user')


class Chat(Base):
    __tablename__ = 'chats'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    collection_id: Mapped[str]
    text: Mapped[str]
    history: Mapped['History'] = relationship('History', backref='chat')


class History(Base):
    __tablename__ = 'history'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    chat_id: Mapped[int] = mapped_column(
        ForeignKey('chats.id', ondelete='CASCADE')
    )
    request: Mapped[str]
    response: Mapped[str]
    created_at: Mapped[str] = mapped_column(DateTime)
