from sqlalchemy.orm import Session
from sqlalchemy import text
from pgvector.asyncpg import register_vector
import pandas as pd
from src.schemas import DocumentModel
from src.database.models import User, Document

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


async def create_index(db: Session):
    """
    Create an index on the 'embedding' column of the 'documents' table.

    :param db: The asynchronous database session.
    """
    try:
        db.execute(
            text(
                "CREATE INDEX idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);"
            )
        )
        db.commit()
        print("Index created successfully.")
    except Exception as e:
        print(f"Error creating index: {e}")

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

    