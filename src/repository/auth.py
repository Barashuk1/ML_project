from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import UserModel
from sqlalchemy import func
from src.schemas import *
from fastapi import HTTPException


async def get_user_by_email(
    email: str,
    db: Session
) -> User:
    """
    Retrieve a user by email from the database.

    :param email: The email address of the user to retrieve.
    :param db: The database session.
    :return: The retrieved user.
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(
    body: UserModel,
    db: Session
) -> User:
    """
    Create a new user in the database.

    :param body: The user data.
    :param db: The database session.
    :return: The created user.
    """
    user_count = db.query(User).count()
    new_user = User(**body.dict())
    new_user.role = 'admin' if user_count == 0 else 'user'
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(
    user: User,
    token: str | None,
    db: Session
) -> None:
    """
    Update the refresh token for a user.

    :param user: The user whose token is being updated.
    :param token: The new refresh token, or None if no token is provided.
    :param db: The database session.
    :return: None
    """
    user.refresh_token = token
    db.commit()
