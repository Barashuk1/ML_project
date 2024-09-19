from sqlalchemy.orm import (
    Mapped, mapped_column, relationship, declarative_base
)
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.dialects import postgresql
from sqlalchemy import String, ForeignKey
from pgvector.sqlalchemy import Vector

Base = declarative_base()

postgresql.VECTOR = Vector


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String(256))
    email: Mapped[str] = mapped_column(String(256))
    password: Mapped[str] = mapped_column(String(256))
    history: Mapped['History'] = relationship('History', backref='user')
    documents: Mapped['Document'] = relationship('Document', backref='user')
    refresh_token: Mapped[str | None]


class Chat(Base):
    __tablename__ = 'chats'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    document_name: Mapped[str]


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


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str]
    tokens: Mapped[int]
    embedding: Mapped[list] = mapped_column(Vector(768))
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')
    )
    document_name: Mapped[str]
