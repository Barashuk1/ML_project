from src.database.models import Document, History, Chat
from src.schemas import DocumentModel
from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime
from sqlalchemy import select


async def get_documents(
    user_id: int,
    db: Session
    ):
    """
    Get all documents from the database.

    :param db: The database session.
    :return: A list of all documents.
    """
    documents = db.query(Chat).filter(Chat.user_id == user_id).all()
    return [document.document_name for document in documents]


async def create_chat(filename, user_id, db: Session):
    new_chat = Chat(document_name=filename, user_id=user_id)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat


async def create_document(body: DocumentModel, db: Session) -> Document:
    """
    Create a new document in the database.

    :param body: The document data.
    :param db: The database session.
    :return: The created document.
    """
    new_document = Document(**body.model_dump())
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    return new_document


async def insert_data_from_dataframe(
    df: pd.DataFrame, filename: str, db: Session
):
    """
    Insert data from a pandas DataFrame into the 'documents' table.

    :param df: The pandas DataFrame containing the data to be inserted.
    :param db: The asynchronous database session.
    """
    for index, row in df.iterrows():
        new_document = Document(
            content=row['content'],
            tokens=row['tokens'],
            embedding=row['embeddings'],
            user_id=row['user_id'],
        )
        new_document.document_name = filename
        db.add(new_document)
    db.commit()


async def get_user_history(user_id, limit, db: Session):

    query = select(History).where(History.user_id == user_id).order_by(History.created_at.desc()).limit(limit)
    result = db.execute(query).scalars().all()
    return result


async def insert_data_history(db: Session, request: str, response: str, user_id: int, document: str):
    doc_id = db.execute(select(Chat).where(Chat.document_name == document)).scalars().first().id
    new_record = History(request=request, response=response, user_id=user_id, created_at=datetime.utcnow(), chat_id=doc_id)
    db.add(new_record)
    db.commit()


async def delete_document(db: Session, user_id: int):
    db_result = db.scalars(select(Document).where(Document.user_id == user_id)).all()
    db_history = db.scalars(select(History).where(History.user_id == user_id)).all()
    for document in db_result:
        db.delete(document)
    for history in db_history:
        db.delete(history)
    db.commit()

