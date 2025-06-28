"""
Authentication and Authorization Module

This module provides functions for user authentication, password hashing,
JWT token creation, and user retrieval from the database.
    * verify_password: Verifies a plain password against a hashed password.
    * get_password_hash: Hashes a plain password using bcrypt.
    * get_user: Retrieves a user from the database by username (email).
    * authenticate_user: Authenticates a user by checking the provided username and password.
    * create_access_token: Creates a JWT access token with an expiration time.
    * get_current_user: Retrieves the current user from the JWT token.
    * get_current_active_user: Checks if the current user is active.

get_current_user and get_current_active_user are FastAPI dependencies
that can be used in route handlers to ensure that the user is authenticated
and active before accessing protected resources.
"""

import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from typing import Annotated
import jwt
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import HTTPException
from sqlmodel import select
from config.database import SessionDep

from schema.auth import TokenData
from schema.user import User

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str, session: SessionDep)  -> User | None:
    """
    Retrieve a user by username (email in this case) from the database.
    """
    stmt = select(User).where(User.email == username)
    user = session.exec(stmt).first()
    if not user:
        return None
    return user


def authenticate_user(username: str, password: str, session: SessionDep):
    """
    Authenticate a user by checking the provided username and password.
    """
    user = get_user(username=username, session=session)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a JWT access token with an expiration time.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ.get("SECRET_KEY"),
                             algorithm=os.environ.get("ALGORITHM"))
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           session: SessionDep):
    """
    Get the current user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.environ.get("SECRET_KEY"),
                             algorithms=[os.environ.get("ALGORITHM")])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username, session=session)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
