INSERT INTO companies (name, industry, country, website, size_category)
VALUES
('Google',      'Technology',  'US', 'https://google.com',     'enterprise'),
('Daraz',       'E-Commerce',  'PK', 'https://daraz.pk',       'sme'),
('Systems Ltd', 'IT Services', 'PK', 'https://systemsltd.com', 'enterprise'),
('Arbisoft',    'Software',    'PK', 'https://arbisoft.com',   'sme'),
('Shopify',     'E-Commerce',  'CA', 'https://shopify.com',    'enterprise');

INSERT INTO sources (name, base_url, is_active)
VALUES
('WeWorkRemotely', 'https://weworkremotely.com', TRUE),
('Rozee.pk',       'https://rozee.pk',           TRUE),
('Remotive',       'https://remotive.com',        TRUE);

INSERT INTO locations (city, country, is_remote)
VALUES
('Lahore',    'PK', FALSE),
('Karachi',   'PK', FALSE),
('Islamabad', 'PK', FALSE),
('New York',  'US', FALSE),
(NULL,        'US', TRUE);

INSERT INTO user_profiles (full_name, email, years_experience, current_title)
VALUES
('Ali Hassan',  'ali@email.com',  2, 'Junior Developer'),
('Sara Khan',   'sara@email.com', 4, 'Python Developer'),
('Umar Farooq', 'umar@email.com', 1, 'Fresh Graduate');

INSERT INTO job_postings (
    title, description, salary_min, salary_max,
    currency, job_type, work_mode, status,
    posted_date, source_url,
    company_id, source_id, location_id
)
VALUES
(
    'Python Backend Developer',
    'We need a Python developer with FastAPI experience.',
    80000, 120000, 'USD', 'full_time', 'remote', 'active',
    '2025-06-01', 'https://weworkremotely.com/job/001',
    1, 1, 5
),
(
    'Data Analyst',
    'Looking for a data analyst with SQL and Python skills.',
    60000, 90000, 'PKR', 'full_time', 'onsite', 'active',
    '2025-06-05', 'https://rozee.pk/job/002',
    2, 2, 1
),
(
    'Full Stack Developer',
    'React and Node.js developer needed for hybrid role.',
    70000, 100000, 'USD', 'full_time', 'hybrid', 'active',
    '2025-06-10', 'https://remotive.com/job/003',
    3, 3, 3
),
(
    'Junior Python Developer',
    'Entry level Python developer for automation tasks.',
    40000, 60000, 'PKR', 'full_time', 'remote', 'active',
    '2025-06-12', 'https://rozee.pk/job/004',
    4, 2, 5
),
(
    'Software Engineer',
    'C++ and Python engineer for systems software.',
    90000, 130000, 'USD', 'contract', 'onsite', 'active',
    '2025-06-15', 'https://weworkremotely.com/job/005',
    5, 1, 4
);

INSERT INTO remote_jobs (job_id, timezone_requirement, async_friendly)
VALUES
(1, 'UTC+5 to UTC+8', TRUE),
(4, 'UTC+5',          TRUE);

INSERT INTO onsite_jobs (job_id, office_address, relocation_package)
VALUES
(2, 'Daraz Office, Lahore, Pakistan', FALSE),
(5, '123 Tech Ave, New York, USA',    TRUE);

INSERT INTO hybrid_jobs (job_id, days_remote_per_week, days_onsite_per_week)
VALUES
(3, 3, 2);

INSERT INTO technical_skills (name, category, skill_type, language_flag, framework_for)
VALUES
('Python',     'Language',  'technical', TRUE,  NULL),
('SQL',        'Database',  'technical', FALSE, NULL),
('FastAPI',    'Framework', 'technical', FALSE, 'Python'),
('React',      'Framework', 'technical', FALSE, 'JavaScript'),
('JavaScript', 'Language',  'technical', TRUE,  NULL),
('PostgreSQL', 'Database',  'technical', FALSE, NULL),
('Git',        'Tool',      'technical', FALSE, NULL);

INSERT INTO soft_skills (name, category, skill_type, competency_area)
VALUES
('Communication',   'Soft', 'soft', 'Communication'),
('Teamwork',        'Soft', 'soft', 'Collaboration'),
('Problem Solving', 'Soft', 'soft', 'Critical Thinking');

-- Job 1 needs Python, SQL, FastAPI
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(1, 1, 'required'),
(1, 2, 'required'),
(1, 3, 'required');

-- Job 2 needs SQL, Python, PostgreSQL
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(2, 2, 'required'),
(2, 1, 'required'),
(2, 6, 'preferred');

-- Job 3 needs React, JavaScript, SQL
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(3, 4, 'required'),
(3, 5, 'required'),
(3, 2, 'preferred');

-- Job 4 needs Python, Git
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(4, 1, 'required'),
(4, 7, 'preferred');

-- Job 5 needs Python, SQL, Git
INSERT INTO job_skills (job_id, skill_id, importance) VALUES
(5, 1, 'required'),
(5, 2, 'required'),
(5, 7, 'required');

-- Ali knows Python, SQL, FastAPI
INSERT INTO user_skills (user_id, skill_id, proficiency_level, years_used) VALUES
(1, 1, 4, 2.0),
(1, 2, 3, 2.0),
(1, 3, 2, 1.0);

-- Sara knows Python, SQL, PostgreSQL, Git
INSERT INTO user_skills (user_id, skill_id, proficiency_level, years_used) VALUES
(2, 1, 5, 4.0),
(2, 2, 4, 4.0),
(2, 6, 3, 2.0),
(2, 7, 3, 3.0);

-- Umar knows JavaScript, React
INSERT INTO user_skills (user_id, skill_id, proficiency_level, years_used) VALUES
(3, 5, 2, 1.0),
(3, 4, 2, 1.0);

INSERT INTO applications (user_id, job_id, status, cover_note, match_score)
VALUES
(1, 1, 'submitted',    'I have 2 years Python and FastAPI experience.', 100.00),
(1, 2, 'interviewing', 'Strong SQL background.',                        66.67),
(2, 2, 'submitted',    'I am a Python and SQL expert.',                 100.00),
(3, 3, 'submitted',    'I know React and JavaScript well.',             66.67);