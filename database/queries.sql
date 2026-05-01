-- ============================================================
-- QUERIES.SQL — Job Intelligence Platform (JIP)
-- All queries, views, triggers, stored procedure in one file
-- ============================================================


-- ============================================================
-- QUERY 1: Basic SELECT with INNER JOIN
-- Get all active jobs with company name and location
-- ============================================================

SELECT
    jp.job_id,
    jp.title,
    jp.job_type,
    jp.work_mode,
    jp.salary_min,
    jp.salary_max,
    jp.currency,
    c.name       AS company_name,
    c.industry,
    l.city,
    l.country
FROM job_postings jp
INNER JOIN companies c  ON jp.company_id  = c.company_id
INNER JOIN locations l  ON jp.location_id = l.location_id
WHERE jp.status = 'active'
ORDER BY jp.posted_date DESC;


-- ============================================================
-- QUERY 2: INNER JOIN with job_skills
-- Get all required skills for every active job
-- ============================================================

SELECT
    jp.job_id,
    jp.title,
    ts.name      AS skill_name,
    js.importance
FROM job_postings jp
INNER JOIN job_skills       js ON jp.job_id    = js.job_id
INNER JOIN technical_skills ts ON js.skill_id  = ts.skill_id
WHERE jp.status = 'active'
ORDER BY jp.job_id;


-- ============================================================
-- QUERY 3: UNION ALL
-- Combine all job types into one single list
-- ============================================================

SELECT
    jp.job_id,
    jp.title,
    'remote'                 AS work_mode,
    rj.timezone_requirement  AS extra_info
FROM job_postings jp
INNER JOIN remote_jobs rj ON jp.job_id = rj.job_id
WHERE jp.status = 'active'

UNION ALL

SELECT
    jp.job_id,
    jp.title,
    'onsite'                 AS work_mode,
    oj.office_address        AS extra_info
FROM job_postings jp
INNER JOIN onsite_jobs oj ON jp.job_id = oj.job_id
WHERE jp.status = 'active'

UNION ALL

SELECT
    jp.job_id,
    jp.title,
    'hybrid'                              AS work_mode,
    CAST(hj.days_remote_per_week AS TEXT) AS extra_info
FROM job_postings jp
INNER JOIN hybrid_jobs hj ON jp.job_id = hj.job_id
WHERE jp.status = 'active';


-- ============================================================
-- QUERY 4: Job Matching Query (MAIN FEATURE)
-- Ranks jobs by skill overlap for a specific user
-- Change user_id = 1 to 2 or 3 to test other users
-- ============================================================

SELECT
    jp.job_id,
    jp.title,
    c.name                                           AS company,
    jp.work_mode,
    jp.salary_min,
    jp.salary_max,
    COUNT(js.skill_id)                               AS total_required,
    COUNT(us.skill_id)                               AS matched_skills,
    ROUND(
        COUNT(us.skill_id) * 100.0
        / NULLIF(COUNT(js.skill_id), 0), 1
    )                                                AS match_percent
FROM job_postings jp
INNER JOIN companies   c  ON jp.company_id = c.company_id
INNER JOIN job_skills  js ON jp.job_id     = js.job_id
LEFT  JOIN user_skills us ON js.skill_id   = us.skill_id
                          AND us.user_id   = 1
WHERE jp.status = 'active'
GROUP BY
    jp.job_id,
    jp.title,
    c.name,
    jp.work_mode,
    jp.salary_min,
    jp.salary_max
ORDER BY match_percent DESC;


-- ============================================================
-- QUERY 5: Correlated Subquery
-- Find jobs where user has ALL required skills (perfect match)
-- ============================================================

SELECT jp.job_id, jp.title
FROM job_postings jp
WHERE NOT EXISTS (
    SELECT 1
    FROM job_skills js
    WHERE js.job_id      = jp.job_id
    AND   js.importance  = 'required'
    AND   NOT EXISTS (
        SELECT 1
        FROM user_skills us
        WHERE us.skill_id = js.skill_id
        AND   us.user_id  = 1
    )
)
AND jp.status = 'active';


-- ============================================================
-- QUERY 6: Window Function
-- Rank jobs by salary within each industry
-- ============================================================

SELECT
    jp.title,
    c.industry,
    jp.salary_max,
    jp.currency,
    RANK() OVER (
        PARTITION BY c.industry
        ORDER BY jp.salary_max DESC NULLS LAST
    ) AS salary_rank
FROM job_postings jp
INNER JOIN companies c ON jp.company_id = c.company_id
WHERE jp.status = 'active';


-- ============================================================
-- QUERY 7: Aggregate Query
-- Top industries by job count and average salary
-- ============================================================

SELECT
    c.industry,
    COUNT(jp.job_id)             AS total_jobs,
    ROUND(AVG(jp.salary_max), 0) AS avg_max_salary
FROM job_postings jp
INNER JOIN companies c ON jp.company_id = c.company_id
WHERE jp.status = 'active'
GROUP BY c.industry
ORDER BY total_jobs DESC;


-- ============================================================
-- QUERY 8: Application History with LEFT JOIN
-- Show all applications for a user with job and company details
-- ============================================================

SELECT
    a.app_id,
    jp.title,
    c.name        AS company,
    a.applied_at,
    a.status,
    a.match_score
FROM applications a
INNER JOIN job_postings jp ON a.job_id      = jp.job_id
INNER JOIN companies    c  ON jp.company_id  = c.company_id
WHERE a.user_id = 1
ORDER BY a.applied_at DESC;


-- ============================================================
-- QUERY 9: UPDATE and DELETE
-- ============================================================

-- Update application status
UPDATE applications
SET    status = 'interviewing'
WHERE  app_id = 1;

-- Verify the update
SELECT app_id, status FROM applications WHERE app_id = 1;

-- Delete expired jobs older than 30 days
DELETE FROM job_postings
WHERE  status     = 'expired'
AND    expiry_date < CURRENT_DATE - INTERVAL '30 days';


-- ============================================================
-- VIEW: vw_job_details
-- Enriched job listing used by the dashboard
-- ============================================================

CREATE VIEW vw_job_details AS
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
    c.name              AS company_name,
    c.industry,
    l.city,
    l.country,
    COUNT(js.skill_id)  AS skills_required
FROM job_postings jp
INNER JOIN companies  c  ON jp.company_id  = c.company_id
INNER JOIN locations  l  ON jp.location_id = l.location_id
LEFT  JOIN job_skills js ON jp.job_id      = js.job_id
GROUP BY
    jp.job_id,
    c.name,
    c.industry,
    l.city,
    l.country;

-- Test the view
SELECT * FROM vw_job_details;


-- ============================================================
-- TRIGGER: Auto expire jobs past their deadline
-- ============================================================

CREATE OR REPLACE FUNCTION fn_expire_jobs()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.expiry_date IS NOT NULL
       AND NEW.expiry_date < CURRENT_DATE THEN
        NEW.status := 'expired';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_expire_jobs
BEFORE INSERT OR UPDATE ON job_postings
FOR EACH ROW EXECUTE FUNCTION fn_expire_jobs();

-- Test the trigger
INSERT INTO job_postings (
    title, description, job_type, work_mode,
    posted_date, expiry_date, source_url,
    company_id, source_id, location_id
) VALUES (
    'Old Expired Job',
    'This job is already past its deadline.',
    'full_time', 'remote',
    '2024-01-01', '2024-06-01',
    'https://test.com/expired/001',
    1, 1, 5
);

-- Verify trigger set status to expired automatically
SELECT job_id, title, status, expiry_date
FROM job_postings
WHERE title = 'Old Expired Job';


-- ============================================================
-- STORED PROCEDURE: sp_apply
-- Calculates match score and saves application in one call
-- ============================================================

CREATE OR REPLACE PROCEDURE sp_apply(
    p_user_id  INT,
    p_job_id   INT,
    p_note     TEXT DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    v_total   INT;
    v_matched INT;
    v_score   NUMERIC(5,2);
BEGIN
    -- Count total required skills for this job
    SELECT COUNT(*) INTO v_total
    FROM job_skills
    WHERE job_id    = p_job_id
    AND   importance = 'required';

    -- Count how many of those the user has
    SELECT COUNT(*) INTO v_matched
    FROM job_skills js
    INNER JOIN user_skills us ON js.skill_id = us.skill_id
    WHERE js.job_id  = p_job_id
    AND   us.user_id = p_user_id;

    -- Calculate percentage score
    v_score := ROUND(
        v_matched * 100.0 / NULLIF(v_total, 0), 2
    );

    -- Insert application record
    INSERT INTO applications (user_id, job_id, cover_note, match_score)
    VALUES (p_user_id, p_job_id, p_note, v_score);

END;
$$;

-- Test the stored procedure
CALL sp_apply(3, 4, 'I am very interested in this Python role.');

-- Verify application was saved with correct score
SELECT * FROM applications WHERE user_id = 3;