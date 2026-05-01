CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    industry VARCHAR(100),
    country CHAR(2) NOT NULL,
    website TEXT,
    size_category VARCHAR(20) CHECK (size_category IN ('startup', 'sme', 'enterprise')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE sources (
    source_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    base_url TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_scraped_at TIMESTAMPTZ
);

CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    city VARCHAR(100),
    country CHAR(2) NOT NULL,
    is_remote BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (city, country, is_remote)
);


CREATE TABLE user_profiles (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    years_experience SMALLINT DEFAULT 0,
    current_title VARCHAR(200),
    bio TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE job_postings (
    job_id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    description TEXT NOT NULL,
    salary_min NUMERIC(10,2),
    salary_max NUMERIC(10,2),
    currency CHAR(3) DEFAULT 'USD',
    job_type VARCHAR(20) NOT NULL CHECK (job_type IN ('full_time','part_time','contract','internship')),
    work_mode VARCHAR(10) NOT NULL CHECK (work_mode IN ('remote','onsite','hybrid')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active','expired','filled')),
    posted_date DATE NOT NULL,
    expiry_date DATE,
    source_url TEXT UNIQUE,
    company_id INT REFERENCES companies(company_id),
    source_id INT REFERENCES sources(source_id),
    location_id INT REFERENCES locations(location_id),
    scraped_at TIMESTAMPTZ DEFAULT NOW()
);


CREATE TABLE remote_jobs (
    job_id INT PRIMARY KEY REFERENCES job_postings(job_id) ON DELETE CASCADE,
    timezone_requirement VARCHAR(50),
    async_friendly BOOLEAN DEFAULT TRUE
);


CREATE TABLE onsite_jobs (
    job_id INT PRIMARY KEY REFERENCES job_postings(job_id) ON DELETE CASCADE,
    office_address TEXT,
    relocation_package BOOLEAN DEFAULT FALSE
);


CREATE TABLE hybrid_jobs (
    job_id INT PRIMARY KEY REFERENCES job_postings(job_id) ON DELETE CASCADE,
    days_remote_per_week SMALLINT CHECK (days_remote_per_week BETWEEN 0 AND 7),
    days_onsite_per_week SMALLINT CHECK (days_onsite_per_week BETWEEN 0 AND 7)
);


CREATE TABLE technical_skills (
    skill_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    skill_type VARCHAR(15) NOT NULL DEFAULT 'technical',
    language_flag BOOLEAN DEFAULT FALSE,
    framework_for VARCHAR(100),
    version_specific VARCHAR(30)
);


CREATE TABLE soft_skills (
    skill_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    skill_type VARCHAR(15) NOT NULL DEFAULT 'soft',
    competency_area VARCHAR(100)
);


CREATE TABLE job_skills (
    job_id INT NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    skill_id INT NOT NULL,
    importance VARCHAR(15) DEFAULT 'required' CHECK (importance IN ('required','preferred','nice_to_have')),
    PRIMARY KEY (job_id, skill_id)
);


CREATE TABLE user_skills (
    user_id INT NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    skill_id INT NOT NULL,
    proficiency_level SMALLINT CHECK (proficiency_level BETWEEN 1 AND 5),
    years_used NUMERIC(4,1),
    PRIMARY KEY (user_id, skill_id)
);


CREATE TABLE applications (
    app_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    job_id INT NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'submitted' CHECK (status IN ('submitted','interviewing','offered','rejected','withdrawn')),
    cover_note TEXT,
    match_score NUMERIC(5,2) CHECK (match_score BETWEEN 0 AND 100),
    UNIQUE (user_id, job_id)
);