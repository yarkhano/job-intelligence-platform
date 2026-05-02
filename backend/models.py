# Each class in this file represents one table in your database. SQLAlchemy
# reads these classes and knows exactly how your tables are structured. These
# models are used when you want to query or insert data using Python objects ,instead of raw SQL strings.

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Numeric, SmallInteger, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Company(Base):
    __tablename__ = "companies"
    company_id = Column(Integer,primary_key=True)
    name = Column(String(100),nullable=False,unique=True)
    industry = Column(String(100))
    country = Column(String(4))
    website =  Column(Text)
    size_category = Column(String(20))
    created_at = Column(DateTime)


class Source(Base):
    __tablename__ = "sources"
    source_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    base_url = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    last_scraped_at = Column(DateTime)


class Location(Base):
    __tablename__ = "locations"
    location_id = Column(Integer, primary_key=True)
    city = Column(String(100))
    country = Column(String(2), nullable=False)
    is_remote = Column(Boolean, nullable=False, default=False)


class JobPosting(Base):
    __tablename__ = "job_postings"
    job_id = Column(Integer, primary_key=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    salary_min = Column(Numeric(10, 2))
    salary_max = Column(Numeric(10, 2))
    currency = Column(String(3), default='USD')
    job_type = Column(String(20), nullable=False)
    work_mode = Column(String(10), nullable=False)
    status = Column(String(20), default='active')
    posted_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    source_url = Column(Text, unique=True)
    company_id = Column(Integer)  # Foreign key to companies
    source_id = Column(Integer)   # Foreign key to sources
    location_id = Column(Integer) # Foreign key to locations
    scraped_at = Column(DateTime)


class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(254), nullable=False, unique=True)
    years_experience = Column(SmallInteger, default=0)
    current_title = Column(String(200))
    bio = Column(Text)
    created_at = Column(DateTime)


class Application(Base):
    __tablename__ = "applications"
    app_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    job_id = Column(Integer, nullable=False)
    applied_at = Column(DateTime)
    status = Column(String(20), default='submitted')
    cover_note = Column(Text)
    match_score = Column(Numeric(5, 2))