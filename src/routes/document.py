from typing import List

from fastapi import (
    APIRouter, Depends, status, UploadFile, File, Query,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import src.repository.document as document_repository
from src.services.text_processing_service import (
    chunk_text_by_sentences, process_text_chunks,
    process_input_with_retrieval, read_pdf
)
from src.schemas import HistoryModel, QuestionRequest
from src.services.auth import auth_service
from src.database.models import User
from src.database.db import get_db

router = APIRouter(prefix='/document', tags=["document"])


@router.get("/documents")
async def get_documents(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The get_documents function returns a list of documents.
    """
    documents = await document_repository.get_documents(current_user.id, db)
    return JSONResponse(content={"documents": documents})


@router.post("/upload_file/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Upload a PDF file, convert its content to text, chunk the text, process the chunks, and insert the data into the database.

    :param file: The uploaded PDF file.
    :param db: The asynchronous database session.
    :param current_user: The current authenticated user.
    :return: A message indicating the success of the operation.
    """

    try:
        filename = file.filename
        await document_repository.create_chat(filename, current_user.id, db)
        # Read the PDF file and convert its content to text
        text = await read_pdf(file)

        # Chunk the text by sentences
        text_chunks = await chunk_text_by_sentences(text)

        # Process the text chunks and create a DataFrame
        df = await process_text_chunks(text_chunks, current_user.id)

        # Insert the data from the DataFrame into the database
        await document_repository.insert_data_from_dataframe(df, filename, db)

        return JSONResponse(content={"message": f"Files uploaded successfully!"})
    except Exception as e:
        return JSONResponse(content={"message": "File upload failed!"}, status_code=500)


@router.post("/chat/")
async def chat(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Process user input by retrieving the most similar documents from the database and generating a response.

    :param user_input: The user input to process.
    :param db: The synchronous database session.
    :param current_user: The current authenticated user.
    :return: The generated response.
    """
    # Process the input with retrieval
    response = await process_input_with_retrieval(*request, current_user.id, db)

    return {"response": response}


@router.get("/history/", response_model=List[HistoryModel])
async def get_history(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, description="Number of history records to return")
):
    """
    Retrieve the most recent history records for the current user.

    :param current_user: The current authenticated user.
    :param db: The asynchronous database session.
    :param limit: The maximum number of history records to return.
    :return: A list of history records.
    """
    history_records = await document_repository.get_user_history(db=db, user_id=current_user.id, limit=limit)
    return history_records


@router.delete("/delete_data", status_code=status.HTTP_202_ACCEPTED)
async def delete_content(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Delete all data from the database.

    :param db: The asynchronous database session.
    :param current_user: The current authenticated user.
    :return: A message indicating the success of the operation.
    """

    return await document_repository.delete_document(db=db, user_id=current_user.id)
