"""
Authentication and Authorization Schemas
This module defines the data models used for authentication and authorization processes.
"""

from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None