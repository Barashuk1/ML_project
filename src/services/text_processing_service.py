from typing import List
import io

from fastapi import UploadFile, File, HTTPException, status
from sentence_transformers import SentenceTransformer
from nltk.tokenize import sent_tokenize
from sqlalchemy.orm import Session
from transformers import pipeline
from tqdm.asyncio import tqdm
from sqlalchemy import text
import pandas as pd
import numpy as np
import tiktoken
import PyPDF2
import nltk

from src.repository.document import insert_data_history

nltk.download('punkt_tab')
nltk.download('punkt')


async def read_pdf(file: UploadFile = File(...)):
    """
    Asynchronously read a PDF file and convert its content to text.

    :param file: The uploaded PDF file.
    :return: The extracted text from the PDF.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a PDF")

    file_content = await file.read()
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"

    return text


async def num_tokens_from_string(string: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens


async def chunk_text_by_sentences(text, max_tokens=100):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_token_count = 0

    for sentence in sentences:
        num_tokens = await num_tokens_from_string(sentence)
        if current_token_count + num_tokens <= max_tokens:
            current_chunk.append(sentence)
            current_token_count += num_tokens
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_token_count = num_tokens

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


async def process_text_chunks(text_chunks, user_id):
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    encoding = tiktoken.get_encoding("cl100k_base")

    data = []
    for text in tqdm(text_chunks):
        num_tokens = len(encoding.encode(text))
        embeddings = model.encode(text, show_progress_bar=False)
        data.append({'user_id': user_id, 'content': text, 'tokens': num_tokens, 'embeddings': embeddings})

    return pd.DataFrame(data)


async def get_embeddings(text):
    """
    Helper function: Get embeddings for a text.

    :param text: The text to get embeddings for.
    :return: The embeddings for the text.
    """
    model = SentenceTransformer('distilbert-base-uncased')
    return model.encode(text)


async def combine_context_and_input(context, user_input):
    return f"User: {user_input}\nAssistant:{context}"


async def get_completion_from_messages(context, user_input, model='distilgpt2', max_tokens=400):
    generator = pipeline('text-generation', model=model)
    combined_text = await combine_context_and_input(context, user_input)
    response = generator(
        combined_text,
        max_new_tokens=max_tokens,
        truncation=True
    )
    response = response[0]['generated_text'].split(']')[1]
    return response

async def get_top3_similar_docs(
        query_embedding: np.ndarray,
        user_id: int,
        document_name: str,
        db: Session,
        limit: int = 3
) -> List[str]:
    """
    Get top similar documents based on the query embedding.

    :param query_embedding: The query embedding as a list of floats.
    :param user_id: The user ID to filter documents.
    :param db: The async database session.
    :param limit: The number of similar documents to return (default is 5).
    :return: A list of tuples containing the content of similar documents.
    """

    query_embedding = query_embedding.flatten().tolist()[:768]

    query = text("""
    SELECT content
    FROM documents
    WHERE user_id = :user_id
    AND document_name = :document_name
    ORDER BY embedding <=> CAST(:query_vector AS vector)
    LIMIT :limit
    """)

    result = db.execute(
        query,
        {
            "user_id": user_id,
            "query_vector": query_embedding,
            "limit": limit,
            "document_name": document_name
        }
    )

    return result.fetchall()



async def process_input_with_retrieval(document, question, user_id: int,
        db: Session) -> str:
    related_docs = await get_top3_similar_docs(await get_embeddings(question), user_id, document[1], db)

    context = f"Relevant information: {related_docs}"

    response = await get_completion_from_messages(context, question)
    await insert_data_history(db, question, response, user_id, document[1])
    return response
