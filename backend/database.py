import os
from dotenv import load_dotenv
from sqlalchemy import create_engine #use to connect to database
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL) #This is the actual connection to postgres

SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)

Base = declarative_base() #EVery model createe in model.py will inherit from from this Base

#This function will be used by all your route functions to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db     #this gives the database session to whoever calls this function
    except Exception as e:
        db.rollback()
        print(f"error is :{e}")
    finally:
        db.close()

