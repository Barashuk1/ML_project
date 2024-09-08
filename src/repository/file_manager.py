import os
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from src.database.models import Chat, User  # Упевніться, що імпорт правильний
from PyPDF2 import PdfFileReader
import fitz  # PyMuPDF
import tempfile  # Добавляем этот импорт


UPLOAD_FOLDER = "/uploads"

def create_user(db: Session, user_name: str, email: str, password: str) -> User:
    new_user = User(
        user_name=user_name,
        email=email,
        password=password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


async def save_pdf_file(file: UploadFile, user_id: int, chat_id: int, db: Session):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400, detail="Invalid file format. Only PDF allowed")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        user = User(id=user_id, user_name="New User", email="", password="")
        db.add(user)
        db.commit()
        db.refresh(user)

    # Чтение содержимого файла в памяти
    content = await file.read()

    # Временно сохраняем файл
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        # Извлечение текста из временно сохранённого PDF
        text = extract_text_from_pdf(temp_file_path)

        # Создание чата и запись текста
        chat = Chat(id=chat_id, user_id=user_id,
                    collection_id="some_collection", text=text)
        db.add(chat)
        db.commit()

    finally:
        # Удаление временного файла
        os.remove(temp_file_path)



#    """Витягує текст з PDF-файлу."""
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error extracting text from PDF: {str(e)}")
    return text

# Функція для видалення PDF
# def delete_pdf_file(filename):
#     file_path = os.path.join(UPLOAD_FOLDER, filename)
#     if os.path.exists(file_path):
#         os.remove(file_path)
#     else:
#         raise HTTPException(status_code=404, detail="File not found")


def get_pdf_text(user_id: int, chat_id: int, db: Session):
    chat = db.query(Chat).filter(
        Chat.user_id == user_id, Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return {"text": chat.text}
