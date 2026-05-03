# It creates the FastAPI application, registers all your routers,
# so the Streamlit frontend can talk to this backend.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # It allows your frontend (running on a different port) to make requests to your FastAPI backend without the browser blocking it.
from routes import jobs, applications, users
from database import Base, engine

Base.metadata.create_all(bind=engine)  # This tells SQLAlchemy to create any tables that do not exist yet

app = FastAPI(
    title="Job Intelligence Platform API",
    description="Backend API for JIP — job matching and analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,          # ← this was the only fix — it was missing
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(jobs.router)
app.include_router(users.router)
app.include_router(applications.router)