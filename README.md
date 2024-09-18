 # ML Project


This project is built using FastAPI and provides the following features:

**Uploading PDF** files and extracting text from them.
**Tokenizing text** into sentences and splitting them into chunks based on token count.
**Using the SentenceTransformer** model to generate text embeddings.
**Retrieving** relevant documents based on user queries.
**Generating responses** to user queries using GPT models.
User registration, authentication, and JWT token refresh.


## Installation

## Clone the repository:

1. Clone the repository:

```bash
git clone https://github.com/Barashuk1/ML_project
cd ML_project
```

2. Create a virtual environment (recommended) and activate it:

```bash
python -m venv env
source env/bin/activate   # For Linux/Mac
.\env\Scripts\activate    # For Windows
Install the dependencies:

pip install -r requirements.txt
```

3. Configure environment variables (e.g., in a .env file):

```bash
SECRET_KEY
ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
redis_host
redis_port
Other database connection settings.
Download the necessary NLTK packages:


python -c "import nltk; nltk.download('punkt')"
```


4. Run the FastAPI server:
```bash

uvicorn main:app --reload


Main endpoints:

POST /auth/signup – User registration.
POST /auth/login – User login, returns JWT tokens.
GET /auth/refresh_token – Refresh access token.
POST /upload – Upload a PDF file for text extraction.
POST /question – Process user queries for a document.
POST /submit_register – Register a new user.
POST /submit_login – User login.
Key Features
```


1. ## User Authentication
Users can register and log in to access platform features.

**User registration**: The /auth/signup endpoint allows registering new users. Upon successful registration, it returns user information.
**User login**: The /auth/login endpoint allows users to log in, returning JWT access and refresh tokens.
**Token refresh**: The /auth/refresh_token endpoint allows obtaining a new access token using a refresh token.

2. ## PDF Processing
**PDF Upload**: The read_pdf function asynchronously reads a PDF file and converts its content to text.
**Text Tokenization**: The chunk_text_by_sentences function breaks text into sentences and groups them into chunks based on token count.
**Getting Embeddings**: Using the SentenceTransformer model, the system generates text embeddings, which are used to search for similar documents.
**Generating Responses**: Based on the user query and context from documents, a response is generated using a GPT model.

## Example Usage

**User Registration:**

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/signup' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
User Login:
```

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=&username=user@example.com&password=password&scope=&client_id=&client_secret='
Token Refresh:
```

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/auth/refresh_token' \
  -H 'Authorization: Bearer <refresh_token>'
File Upload:
```
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/upload' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@your_document.pdf'
Querying a Document:
```

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/question' \
  -H 'accept: application/json' \
  -d '{"document": "doc1.pdf", "question": "What is this document about?"}'
Project Structure
main.py – The main file that initializes FastAPI and includes the primary routes.
src/routes – Contains logic for authentication and document-related operations.
src/services – Services for generating tokens and handling user requests.
src/database – Database models and functions to interact with the database.
```




