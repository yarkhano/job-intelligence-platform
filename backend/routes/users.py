from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from database import get_db

class UserCreate(BaseModel):
    ful_name: str
    email: str
    years_experience: int = 0
    bio: Optional[str] = None
