from typing import List

import tiktoken
import pandas as pd
import numpy as np
from sqlalchemy import text
from tqdm.asyncio import tqdm
from sentence_transformers import SentenceTransformer
import nltk
from transformers import pipeline
from sqlalchemy.orm import Session
#from src.repository.file_manager import extract_text_from_pdf
nltk.download('punkt')
from nltk.tokenize import sent_tokenize


async def num_tokens_from_string(string: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens

async def chunk_text_by_sentences(text, max_tokens=150):
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
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    return model.encode(text)


async def combine_context_and_input(context, user_input):
    return f"User: {user_input}\nAssistant:{context}"

async def get_completion_from_messages(context, user_input, model='distilgpt2', max_tokens=850):
    generator = pipeline('text-generation', model=model)
    combined_text = await combine_context_and_input(context, user_input)
    response = generator(
        combined_text,
        max_new_tokens=max_tokens,
        truncation=True
    )
    return response[0]['generated_text']


async def get_top3_similar_docs(
        query_embedding: List[float],
        user_id: int,
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
    embedding_array = np.array(query_embedding)

    query = text("""
    SELECT content 
    FROM documents 
    WHERE user_id = :user_id 
    ORDER BY embedding <=> %s
    LIMIT :limit
    """,  (embedding_array,))

    result = db.execute(query)
    return result.fetchall()


async def process_input_with_retrieval(user_input, user_id: int,
        db: Session) -> str:
    # Step 1: Get documents related to the user input from database
    related_docs = await get_top3_similar_docs(await get_embeddings(user_input), user_id, db)

    # Step 2: Create context from related documents
    context = f"Relevant information: {related_docs[0][0]} {related_docs[1][0]} {related_docs[2][0]} "

    # Step 3: Generate response using the context and user input
    response = await get_completion_from_messages(context, user_input)
    return response

