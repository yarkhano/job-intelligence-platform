from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, Field
from typing import Optional
from database import get_db

class UserCreate(BaseModel):
    full_name: str                          # was "ful_name" — typo fixed
    email: str
    years_experience: int = 0
    current_title: Optional[str] = None    # was missing from original
    bio: Optional[str] = None

class UserSkillCreate(BaseModel):
    skill_id: int
    proficiency_level: int = Field(..., ge=1, le=5)
    years_used: Optional[float] = 0.0      # changed int → float per spec

router = APIRouter(prefix="/users", tags=["Users"])  # prefix= keyword was missing

@router.post("/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    query = text("""
        INSERT INTO user_profiles (full_name, email, years_experience, current_title, bio)
        VALUES (:full_name, :email, :years_experience, :current_title, :bio)
    """)
    db.execute(query, {
        "full_name": user.full_name,
        "email": user.email,
        "years_experience": user.years_experience,
        "current_title": user.current_title,
        "bio": user.bio
    })
    db.commit()  # save changes to database
    return {"message": "User created successfully"}

@router.get("/{user_id}")                   # was missing closing brace
async def get_user(user_id: int, db: Session = Depends(get_db)):  # params were swapped
    query = text("SELECT * FROM user_profiles WHERE user_id = :user_id")
    result = db.execute(query, {"user_id": user_id}).mappings().first()

    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    # second query to get all skills for this user
    skills_query = text("""
        SELECT skill_id, proficiency_level, years_used
        FROM user_skills
        WHERE user_id = :user_id
    """)
    skills = db.execute(skills_query, {"user_id": user_id}).mappings().all()

    return {"user": dict(result), "skills": list(skills)}

@router.post("/{user_id}/skills")
async def add_skill(user_id: int, skill: UserSkillCreate, db: Session = Depends(get_db)):
    query = text("""
        INSERT INTO user_skills (user_id, skill_id, proficiency_level, years_used)
        VALUES (:user_id, :skill_id, :proficiency_level, :years_used)
    """)
    db.execute(query, {
        "user_id": user_id,
        "skill_id": skill.skill_id,
        "proficiency_level": skill.proficiency_level,
        "years_used": skill.years_used
    })
    db.commit()  # save changes to database
    return {"message": "Skill added successfully"}