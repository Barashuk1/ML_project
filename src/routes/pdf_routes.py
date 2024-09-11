# from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
# from fastapi.responses import JSONResponse
# from sqlalchemy.orm import Session
# from src.repository.file_manager import save_pdf_file, create_user, get_pdf_text
# from src.database.db import get_db
# from src.database.models import Chat
# from src.repository import file_manager

# pdf_router = APIRouter(prefix='pdf', tags=['pdf'])


# @pdf_router.post("/users/")
# def create_user_endpoint(
#     user_name: str,
#     email: str,
#     password: str,
#     db: Session = Depends(get_db)
# ):
#     user = create_user(db, user_name, email, password)
#     return {"user_id": user.id}


# # 1. Завантаження PDF
# @pdf_router.post("/upload/")
# async def upload_pdf(
#     user_id: int,
#     chat_id: int,
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     try:
#         file_path = await save_pdf_file(file, user_id, chat_id, db)
#         return JSONResponse(content={"message": "File uploaded", "file_path": file_path})
#     except HTTPException as e:
#         return JSONResponse(content={"detail": str(e)}, status_code=e.status_code)


# # 2. Видалення PDF
# @pdf_router.delete("/delete/{filename}")
# async def delete_pdf(filename: str):
#     file_manager.delete_pdf_file(filename)
#     return JSONResponse(content={"message": "File deleted"})


# # 4. Отримати PDF для поточного чату
# @pdf_router.get("/pdf/text/")
# async def get_text(user_id: int, chat_id: int, db: Session = Depends(get_db)):
#     return get_pdf_text(user_id, chat_id, db)


# # 5. Обробка запитів до документа
# @pdf_router.get("/process/{filename}")
# async def process_pdf(filename: str):
#     file_manager.check_pdf_exists(filename)
#     return JSONResponse(content={"message": "File found and ready for processing"})


# # Функція для оновлення тексту в таблиці Chat
# def update_chat_text(chat_id: int, text: str, db: Session):
#     chat = db.query(Chat).filter(Chat.id == chat_id).first()
#     if not chat:
#         raise HTTPException(status_code=404, detail="Chat not found")

#     chat.text = text
#     db.commit()
#     db.refresh(chat)

#     return chat.id
