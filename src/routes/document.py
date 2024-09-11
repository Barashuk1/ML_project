from fastapi import (
    APIRouter, HTTPException, Depends, status, UploadFile, File,
)


from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from src.schemas import  DocumentModel, DocumentResponse
from src.repository.document import create_document, insert_data_from_dataframe, create_index
from src.services.text_processing_service import chunk_text_by_sentences, process_text_chunks, \
    process_input_with_retrieval, read_pdf
from src.services.auth import auth_service
router = APIRouter(prefix='/document', tags=["document"])


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(document: DocumentModel, db: Session = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)):
    """
    Create a new document in the database.

    :param document: The document data.
    :param db: The asynchronous database session.
    :param current_user: The current authenticated user.
    :return: The created document.
    """

    document.user_id = current_user.id
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")

    new_document = await create_document(document, db)
    await create_index(db)
    return new_document


@router.post("/upload_file/")
async def upload_file(file: UploadFile = File(...),  db: Session = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)):
    """
    Upload a PDF file, convert its content to text, chunk the text, process the chunks, and insert the data into the database.

    :param file: The uploaded PDF file.
    :param db: The asynchronous database session.
    :param current_user: The current authenticated user.
    :return: A message indicating the success of the operation.
    """
    # Read the PDF file and convert its content to text
    text = await read_pdf(file)

    # Chunk the text by sentences
    text_chunks = await chunk_text_by_sentences(text)

    # Process the text chunks and create a DataFrame
    df = await process_text_chunks(text_chunks, current_user.id)

    # Insert the data from the DataFrame into the database
    await insert_data_from_dataframe(df, db)

    return {"message": "File uploaded and processed successfully"}


@router.post("/chat/")
async def chat(user_input: str, db: Session = Depends(get_db),
               current_user: User = Depends(auth_service.get_current_user)):
    """
    Process user input by retrieving the most similar documents from the database and generating a response.

    :param user_input: The user input to process.
    :param db: The synchronous database session.
    :param current_user: The current authenticated user.
    :return: The generated response.
    """
    # Process the input with retrieval
    response = await process_input_with_retrieval(user_input, current_user.id, db)

    return {"response": response}