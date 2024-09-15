from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class UserModel(BaseModel):
    """
    Pydantic model representing user data used for user creation.

    :param username: The username of the user (min length: 5, max length: 16).
    :type username: str
    :param email: The email address of the user.
    :type email: str
    :param password: The password of the user (min length: 6, max length: 10).
    :type password: str
    """
    user_name: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)

class UserDb(BaseModel):
    """
    Pydantic model representing user data retrieved from the database.

    :param id: The unique identifier of the user.
    :type id: int
    :param username: The username of the user.
    :type username: str
    :param email: The email address of the user.
    :type email: str
    :param created_at: The timestamp when the user was created.
    :type created_at: datetime
    :param role: The role of the user.
    :type role: str
    :param is_active: The status of the user.
    :type is_active: bool
    """
    id: int
    user_name: str
    email: str
    class ConfigDict:
        from_attributes = True

class UserResponse(BaseModel):
    """
    Pydantic model representing the response after user creation.

    :param user: The user data.
    :type user: UserDb
    :param detail: The detail of the response.
    :type detail: str
    """
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
    Pydantic model representing the token data.

    :param access_token: The access token.
    :type access_token: str
    :param refresh_token: The refresh token.
    :type refresh_token: str
    :param token_type: The token type.
    :type token_type: str
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class DocumentModel(BaseModel):
    content: str
    tokens: int
    embedding: List[float]
    user_id: int

class DocumentCreate(DocumentModel):
    pass

class DocumentResponse(DocumentModel):
    id: int

    class ConfigDict:
        from_attributes = True

class HistoryModel(BaseModel):
    request: str
    response: str
    created_at: datetime
    class ConfigDict:
        from_attributes = True


