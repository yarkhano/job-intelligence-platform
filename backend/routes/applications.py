from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from database import get_db

class ApplyRequest(BaseModel):
    user_id: int
    job_id: int
    cover_note: Optional[str] = None

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("/apply")
async def apply_to_job(request: ApplyRequest, db: Session = Depends(get_db)):
    try:
        # calls the stored procedure you created in queries.sql
        query = text("CALL sp_apply(:user_id, :job_id, :cover_note)")
        db.execute(query, {
            "user_id": request.user_id,
            "job_id": request.job_id,
            "cover_note": request.cover_note
        })
        db.commit()
    except Exception as e:
        db.rollback()  # undo any partial changes if something went wrong
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Application submitted successfully"}

@router.get("/{user_id}")
async def get_applications(user_id: int, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            a.app_id,
            jp.title,
            c.name      AS company_name,
            a.applied_at,
            a.status,
            a.match_score
        FROM applications a
        INNER JOIN job_postings jp ON a.job_id      = jp.job_id
        INNER JOIN companies    c  ON jp.company_id  = c.company_id
        WHERE a.user_id = :user_id
        ORDER BY a.applied_at DESC
    """)
    results = db.execute(query, {"user_id": user_id}).mappings().all()
    return list(results)

@router.patch("/{app_id}/status")
async def update_status(app_id: int, status: str, db: Session = Depends(get_db)):
    query = text("UPDATE applications SET status = :status WHERE app_id = :app_id")
    db.execute(query, {"status": status, "app_id": app_id})
    db.commit()
    return {"message": "Status updated successfully"}