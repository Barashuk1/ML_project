from src.database.models import Document
from src.schemas import DocumentModel
from sqlalchemy.orm import Session
import pandas as pd


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


async def read_pdf(file_content, user_id, db: Session):

    pdf_reader = PyPDF2.PdfFileReader(io.BytesIO(file_content))
    text = ""

    # Извлекаем текст из всех страниц PDF
    for page_num in range(pdf_reader.getNumPages()):
        page = pdf_reader.getPage(page_num)
        text += page.extract_text()

    return text
