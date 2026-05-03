#It creates the FastAPI application, registers all your routers,so the Streamlit frontend can talk to this backend.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  #It allows your frontend (running on a different port) to make requests to your FastAPI backend without the browser blocking it.
from routes import jobs,applications,users
from database import Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI()