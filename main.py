from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as aioredis
from fastapi import FastAPI, File, UploadFile, HTTPException, status, Depends
import uvicorn
import aiofiles
import shutil, os
from sqlalchemy.orm import Session
from src.database.models import User
from src.database.db import get_db
from src.services.auth import auth_service
from src.routes import auth, document
from src.conf.config import settings
from src.schemas import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    # r = aioredis.from_url(
    #     settings.redis_docker_url,
    #     encoding="utf-8",
    #     decode_responses=True
    # )
    r = aioredis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
    )
    await FastAPILimiter.init(r)

    yield
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)

origins = ["*"]

app.include_router(auth.router, prefix='/ml_project')
app.include_router(document.router, prefix='/ml_project')

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    The read_root function returns the HTML page.
    """
    async with aiofiles.open("src/services/templates/chat.html", mode="r") as file:
        html_content = await file.read()
    return HTMLResponse(content=html_content)

@app.get("/documents")
async def get_documents():
    """
    The get_documents function returns a list of documents.
    """
    documents = ['doc1.pdf', 'doc2.pdf', 'doc3.pdf']
    return JSONResponse(content={"documents": documents})

@app.post("/question")
async def ask_question(request: QuestionRequest):
    # ВСТАВЬТЕ ОБРАБОТКУ ВОПРОСА
    document = request.document
    question = request.question

    return {"answer": f"Your question was: '{question}' for document: '{document}'"}

@app.post("/upload")
async def upload_file(files: list[UploadFile] = File(...)):
    try:
        # ЛОГИКА СОХРАНЕНИЯ ФАЙЛА
        return JSONResponse(content={"message": f"Files uploaded successfully!"})
    except Exception as e:
        return JSONResponse(content={"message": "File upload failed!"}, status_code=500)

@app.get('/register', response_class=HTMLResponse)
async def read_root():
    async with aiofiles.open("src/services/templates/registration.html", mode="r") as file:
        html_content = await file.read()
        print(html_content)
    return HTMLResponse(content=html_content)

@app.post("/submit_register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    new_user = User(
        email=request.email,
        password=auth_service.get_password_hash(request.password),
        user_name=request.email.split('@')[0],
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return JSONResponse(content={"message": "Registration successful!"})

@app.get('/login', response_class=HTMLResponse)
async def read_root():
    async with aiofiles.open("src/services/templates/login.html", mode="r") as file:
        html_content = await file.read()
        print(html_content)
    return HTMLResponse(content=html_content)

@app.post("/submit_login")
async def login(request: RegisterRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )

    if not auth_service.verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password"
        )
    
    return JSONResponse(content={"success": True})
    

if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host='localhost',
        port=8000,
        reload=True,
    )
