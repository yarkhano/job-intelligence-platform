# This file contains all the URL endpoints that the frontend or anyone else
# can call to get job data. When someone visits /jobs in the browser the
# code in this file runs and returns job data as JSON.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/")
def get_all_jobs(db: Session = Depends(get_db)):
    query = text("""
        SELECT
            jp.job_id,
            jp.title,
            jp.work_mode,
            jp.job_type,
            jp.salary_min,
            jp.salary_max,
            jp.currency,
            jp.status,
            jp.posted_date,
            c.name      AS company_name,
            l.city,
            l.country
        FROM job_postings jp
        INNER JOIN companies c  ON jp.company_id  = c.company_id
        INNER JOIN locations l  ON jp.location_id = l.location_id
        WHERE jp.status = 'active'
        ORDER BY jp.posted_date DESC
    """)
    results = db.execute(query)
    return results.mappings().all()


@router.get("/match/{user_id}")
def get_matched_jobs(user_id: int, db: Session = Depends(get_db)):
    query = text("""
        SELECT
            jp.job_id,
            jp.title,
            c.name                                      AS company_name,
            jp.work_mode,
            jp.salary_min,
            jp.salary_max,
            COUNT(js.skill_id)                          AS total_required,
            COUNT(us.skill_id)                          AS matched_skills,
            ROUND(
                COUNT(us.skill_id) * 100.0
                / NULLIF(COUNT(js.skill_id), 0),
                2
            )                                           AS match_percent
        FROM job_postings jp
        INNER JOIN companies  c  ON jp.company_id = c.company_id
        INNER JOIN job_skills  js ON jp.job_id     = js.job_id
        LEFT  JOIN user_skills us ON js.skill_id   = us.skill_id
                                  AND us.user_id   = :user_id
        WHERE jp.status = 'active'
        GROUP BY
            jp.job_id,
            jp.title,
            c.name,
            jp.work_mode,
            jp.salary_min,
            jp.salary_max
        ORDER BY match_percent DESC
    """)
    results = db.execute(query, {"user_id": user_id})
    return results.mappings().all()


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT
                jp.*,
                c.name  AS company_name,
                l.city,
                l.country
            FROM job_postings jp
            INNER JOIN companies c ON jp.company_id  = c.company_id
            INNER JOIN locations l ON jp.location_id = l.location_id
            WHERE jp.job_id = :job_id
        """)
        result = db.execute(query, {"job_id": job_id}).mappings().first()

        if result is None:
            raise HTTPException(status_code=404, detail="Job not found")

        return dict(result)

    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


