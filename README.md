# Job Intelligence Platform (JIP)

> A data-driven job matching and analytics system that automatically collects job postings, stores them in a normalised PostgreSQL database, and matches them to users based on skill overlap.

---

## What is JIP?

JIP is a full-stack web application built as a Database Management Systems semester project. It scrapes job postings from multiple job boards every 24 hours, stores them in a well-organised relational database, and helps job seekers find the most relevant opportunities based on their skills — without manually reading hundreds of listings.

The matching engine uses pure SQL JOIN queries to calculate a match percentage between the user's skill set and each job's required skills. No AI. No black box. Just clean, readable SQL.

---

## Features

- **Automated Scraping** — Playwright scraper collects jobs from WeWorkRemotely, Rozee.pk, and Remotive every 24 hours
- **Skill-Based Matching** — SQL JOIN query ranks every active job by how many of the user's skills it requires
- **Application Tracker** — users apply directly from the platform and track status from submitted to offered
- **Analytics Dashboard** — charts for top hiring industries, in-demand skills, salary ranges, and work mode distribution
- **Auto Expiry** — database trigger automatically marks jobs as expired when their deadline passes
- **Duplicate Prevention** — unique constraint on source URL ensures no job is inserted twice

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Database | PostgreSQL 16 |
| Scraping | Python · Playwright |
| Backend API | Python · FastAPI · SQLAlchemy |
| Frontend | Streamlit |
| Server | Uvicorn |

---

## Database Design

The database has **13 tables** implementing two EERD inheritance hierarchies:

- **TPT (Table Per Type)** for job postings — `job_postings` parent with `remote_jobs`, `onsite_jobs`, `hybrid_jobs` subclass tables
- **TPC (Table Per Concrete Class)** for skills — `technical_skills` and `soft_skills` each contain all parent attributes

**All tables normalised to 3NF.**

| Category | Tables |
|----------|--------|
| Strong Entities | `companies`, `sources`, `locations`, `user_profiles`, `job_postings` |
| TPT Subclasses | `remote_jobs`, `onsite_jobs`, `hybrid_jobs` |
| TPC Subclasses | `technical_skills`, `soft_skills` |
| Junction Tables | `job_skills`, `user_skills`, `applications` |

---

## Project Structure

```
job_intelligence_platform/
│
├── database/
│   ├── schema.sql          # All CREATE TABLE statements
│   ├── seed_data.sql       # Sample data for testing
│   └── queries.sql         # Joins, views, triggers, stored procedure
│
├── backend/
│   ├── main.py             # FastAPI app entry point
│   ├── database.py         # PostgreSQL connection
│   ├── models.py           # SQLAlchemy table models
│   └── routes/
│       ├── jobs.py         # Job listing and search endpoints
│       ├── users.py        # User profile endpoints
│       └── applications.py # Apply and track endpoints
│
├── scraper/
│   └── scraper.py          # Playwright scraper
│
├── frontend/
│   └── dashboard.py        # Streamlit dashboard
│
├── requirements.txt
└── .env.example            # Environment variable template
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 16

### Installation

```bash
# Clone the repository
git clone https://github.com/yarkhano/job-intelligence-platform.git
cd job-intelligence-platform

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

### Database Setup

```bash
# Create the database in PostgreSQL
createdb jip_db

# Run the schema to create all 13 tables
psql -U postgres -d jip_db -f database/schema.sql

# Load sample data
psql -U postgres -d jip_db -f database/seed_data.sql
```

### Environment Variables

Create a `.env` file in the root folder:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=jip_db
DB_USER=postgres
DB_PASSWORD=your_password
```

### Run the Application

```bash
# Start the FastAPI backend
uvicorn backend.main:app --reload

# In a new terminal, start the Streamlit dashboard
streamlit run frontend/dashboard.py

# In a new terminal, run the scraper manually
python scraper/scraper.py
```

- API runs at `http://localhost:8000`
- Dashboard runs at `http://localhost:8501`
- API docs at `http://localhost:8000/docs`

---

## How Job Matching Works

1. User creates a profile and adds their skills with proficiency levels
2. System runs a UNION ALL across all three job type tables to get every active job
3. An INNER JOIN connects jobs to their required skills via `job_skills`
4. A LEFT JOIN compares those required skills against the user's skills in `user_skills`
5. COUNT aggregates how many skills overlap and calculates a match percentage
6. Results are ordered from highest match to lowest

```sql
-- Simplified matching query
SELECT job_id, title, company,
       COUNT(us.skill_id) * 100.0 / COUNT(js.skill_id) AS match_percent
FROM all_jobs
JOIN companies  ON ...
JOIN job_skills js ON ...
LEFT JOIN user_skills us ON js.skill_id = us.skill_id AND us.user_id = ?
GROUP BY job_id, title, company
ORDER BY match_percent DESC;
```

---

## DBMS Concepts Covered

| Concept | Implementation |
|---------|---------------|
| DDL | All 13 table definitions with constraints |
| DML | Scraper inserts, status updates, deletions |
| ERD | 9 entities, 6 relationships |
| EERD | 2 specialisation hierarchies (TPT + TPC) |
| ERM | Full relational mapping |
| Normalisation | 1NF, 2NF, 3NF across all tables |
| INNER JOIN | Jobs ↔ companies, jobs ↔ job_skills |
| LEFT JOIN | job_skills ↔ user_skills for matching |
| UNION ALL | Combine remote, onsite, hybrid job tables |
| Subquery | Correlated NOT EXISTS for perfect match |
| Window Function | RANK() salary comparison within industry |
| Views | Unified active job listing view |
| Triggers | Auto-expire jobs past deadline |
| Stored Procedure | sp_apply() — calculates score and saves application |
| Indexes | On status, company_id, posted_date for query speed |

---

## Project Status

> Academic semester project — in active development.

- [x] Database schema design
- [x] ERD, EERD, ERM diagrams
- [ ] schema.sql implementation
- [ ] Scraper
- [ ] FastAPI backend
- [ ] Streamlit dashboard

---

## Author

Built by a CS student as a DBMS semester project.  
Stack: PostgreSQL · Python · FastAPI · Streamlit · Playwright

---

## License

This project is for academic purposes.
