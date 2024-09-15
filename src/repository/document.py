from src.database.models import Document, History
from src.schemas import DocumentModel
from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime
from sqlalchemy import select


async def create_document(body: DocumentModel, db: Session) -> Document:
    """
    Create a new document in the database.

    :param body: The document data.
    :param db: The database session.
    :return: The created document.
    """
    new_document = Document(**body.dict())
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    return new_document


async def insert_data_from_dataframe(df: pd.DataFrame, db: Session):
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
            user_id=row['user_id']
        )
        db.add(new_document)
    db.commit()


async def get_user_history(user_id, limit, db: Session):

    query = select(History).where(History.user_id == user_id).order_by(History.created_at.desc()).limit(limit)
    result = db.execute(query).scalars().all()
    return result


async def insert_data_history(db: Session, request: str, response: str, user_id: int):
    new_record = History(request=request, response=response, user_id=user_id, created_at=datetime.utcnow())
    db.add(new_record)
    db.commit()


async def delete_document(db: Session, user_id: int):
    db_result = db.scalars(select(Document).where(Document.user_id == user_id)).all()
    db_history = db.scalars(select(History).where(History.user_id == user_id)).all()
    for document in documents:
        db.delete(db_result)
    for history in histories:
        db.delete(db_history)
    db.commit()

