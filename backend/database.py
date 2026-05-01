import os
from dotenv import load_dotenv
from sqlalchemy import create_engine #use to connect to database
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

