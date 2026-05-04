import time
import requests
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
from playwright.sync_api import sync_playwright

load_dotenv()

# ═══════════════════════════════════════════
# DATABASE CONNECTION
# ═══════════════════════════════════════════

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

# ═══════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════

def get_source_id(cursor, source_name):
    cursor.execute("SELECT source_id FROM sources WHERE name = %s", (source_name,))
    result = cursor.fetchone()
    return result[0] if result else None


def get_or_create_company(cursor, conn, company_name):
    cursor.execute("SELECT company_id FROM companies WHERE name = %s", (company_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute(
        "INSERT INTO companies (name, country) VALUES (%s, %s) RETURNING company_id",
        (company_name, 'US')
    )
    company_id = cursor.fetchone()[0]
    conn.commit()
    return company_id


def get_or_create_location(cursor, conn, is_remote=True, city=None, country='US'):
    if is_remote:
        cursor.execute(
            "SELECT location_id FROM locations WHERE is_remote = TRUE",
            ()
        )
        result = cursor.fetchone()
        if result:
            return result[0]
        cursor.execute(
            "INSERT INTO locations (city, country, is_remote) VALUES (%s, %s, %s) RETURNING location_id",
            (None, country, True)
        )
        location_id = cursor.fetchone()[0]
        conn.commit()
        return location_id
    else:
        cursor.execute(
            "SELECT location_id FROM locations WHERE city = %s AND country = %s AND is_remote = FALSE",
            (city, country)
        )
        result = cursor.fetchone()
        if result:
            return result[0]
        cursor.execute(
            "INSERT INTO locations (city, country, is_remote) VALUES (%s, %s, %s) RETURNING location_id",
            (city, country, False)
        )
        location_id = cursor.fetchone()[0]
        conn.commit()
        return location_id


def insert_job(cursor, conn, title, description, company_id,
               source_id, location_id, source_url, job_type, work_mode,
               salary_min=None, salary_max=None):
    try:
        cursor.execute("""
            INSERT INTO job_postings (
                title, description, company_id, source_id, location_id,
                source_url, job_type, work_mode, salary_min, salary_max,
                posted_date, status, scraped_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (source_url) DO NOTHING
        """, (
            title, description, company_id, source_id, location_id,
            source_url, job_type, work_mode, salary_min, salary_max,
            datetime.now().date(), 'active', datetime.now()
        ))
        conn.commit()
        print(f"  Inserted: {title} at {company_id}")
    except Exception as e:
        conn.rollback()
        print(f"  Error inserting job: {e}")


# ═══════════════════════════════════════════
# SCRAPER 1 — WeWorkRemotely (Playwright)
# ═══════════════════════════════════════════

def scrape_weworkremotely():
    print("\n--- Starting WeWorkRemotely Scraper ---")

    conn = get_connection()
    cursor = conn.cursor()

    source_id = get_source_id(cursor, "WeWorkRemotely")
    if not source_id:
        print("ERROR: WeWorkRemotely not found in sources table. Run seed_data.sql first.")
        conn.close()
        return

    URL = (
        "https://weworkremotely.com/remote-jobs/search?"
        "categories%5B%5D=2&categories%5B%5D=17&categories%5B%5D=18"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Set a real user agent so site does not block us
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

        print(f"Opening browser and visiting: {URL}")
        page.goto(URL)

        # Wait 5 seconds for full page load including JavaScript
        print("Waiting 5 seconds for page to fully load...")
        time.sleep(5)

        # Find all job listing cards using the selector from the HTML you shared
        job_cards = page.query_selector_all("li.new-listing-container")
        print(f"Found {len(job_cards)} job cards on page")

        jobs_inserted = 0
        jobs_skipped = 0

        for card in job_cards:
            try:
                # ── Get job title ──────────────────────────────
                title_el = card.query_selector("h3.new-listing__header__title span.new-listing__header__title__text")
                if not title_el:
                    jobs_skipped += 1
                    continue
                title = title_el.inner_text().strip()
                if not title:
                    jobs_skipped += 1
                    continue

                # ── Get company name ───────────────────────────
                company_el = card.query_selector("p.new-listing__company-name")
                company_name = company_el.inner_text().strip() if company_el else "Unknown"
                # Remove any trailing icon text that gets picked up
                company_name = company_name.replace("View Company Profile", "").strip()

                # ── Get job URL ────────────────────────────────
                link_el = card.query_selector("a.listing-link--unlocked")
                if not link_el:
                    link_el = card.query_selector("a")
                if not link_el:
                    jobs_skipped += 1
                    continue
                href = link_el.get_attribute("href")
                if not href:
                    jobs_skipped += 1
                    continue
                source_url = "https://weworkremotely.com" + href

                # ── Get job type from categories ───────────────
                job_type = 'full_time'  # default
                category_els = card.query_selector_all("p.new-listing__categories__category")
                for cat_el in category_els:
                    cat_text = cat_el.inner_text().strip().lower()
                    if 'full-time' in cat_text or 'full time' in cat_text:
                        job_type = 'full_time'
                    elif 'contract' in cat_text:
                        job_type = 'contract'
                    elif 'part-time' in cat_text or 'part time' in cat_text:
                        job_type = 'part_time'

                # ── All WWR jobs are remote ────────────────────
                work_mode = 'remote'

                # ── Get or create company and location ─────────
                company_id  = get_or_create_company(cursor, conn, company_name)
                location_id = get_or_create_location(cursor, conn, is_remote=True)

                # ── Insert the job ─────────────────────────────
                insert_job(
                    cursor, conn,
                    title=title,
                    description=f"Job posted on WeWorkRemotely. Visit {source_url} for full description.",
                    company_id=company_id,
                    source_id=source_id,
                    location_id=location_id,
                    source_url=source_url,
                    job_type=job_type,
                    work_mode=work_mode
                )
                jobs_inserted += 1

                # Wait 1 second between each job to avoid being blocked
                time.sleep(1)

            except Exception as e:
                print(f"  Error processing card: {e}")
                jobs_skipped += 1
                continue

        browser.close()

    cursor.close()
    conn.close()

    print(f"\nWeWorkRemotely done.")
    print(f"  Jobs inserted : {jobs_inserted}")
    print(f"  Jobs skipped  : {jobs_skipped}")


# ═══════════════════════════════════════════
# SCRAPER 2 — Remotive (Free JSON API)
# ═══════════════════════════════════════════

def scrape_remotive():
    print("\n--- Starting Remotive API Scraper ---")

    conn = get_connection()
    cursor = conn.cursor()

    source_id = get_source_id(cursor, "Remotive")
    if not source_id:
        print("ERROR: Remotive not found in sources table. Run seed_data.sql first.")
        conn.close()
        return

    # Free public API — no key needed
    API_URL = "https://remotive.com/api/remote-jobs?search=python&limit=50"

    print(f"Calling Remotive API: {API_URL}")
    response = requests.get(API_URL, timeout=15)

    if response.status_code != 200:
        print(f"ERROR: API returned status {response.status_code}")
        conn.close()
        return

    data = response.json()
    jobs = data.get("jobs", [])
    print(f"Found {len(jobs)} jobs from Remotive API")

    jobs_inserted = 0
    jobs_skipped  = 0

    for job in jobs:
        try:
            title        = job.get("title", "").strip()
            company_name = job.get("company_name", "Unknown").strip()
            source_url   = job.get("url", "").strip()
            description  = job.get("description", "").strip()
            salary_str   = job.get("salary", "") or ""
            pub_date     = job.get("publication_date", "")

            # Map job type
            raw_type = job.get("job_type", "full_time")
            type_map = {
                "full_time": "full_time",
                "contract":  "contract",
                "part_time": "part_time",
                "freelance": "contract",
                "internship":"internship"
            }
            job_type = type_map.get(raw_type, "full_time")

            if not title or not source_url:
                jobs_skipped += 1
                continue

            # Parse salary range if available
            salary_min = None
            salary_max = None
            if salary_str and "$" in salary_str:
                parts = salary_str.replace("$", "").replace(",", "").split("-")
                try:
                    if len(parts) >= 2:
                        salary_min = float(parts[0].strip().split()[0])
                        salary_max = float(parts[1].strip().split()[0])
                except:
                    pass

            company_id  = get_or_create_company(cursor, conn, company_name)
            location_id = get_or_create_location(cursor, conn, is_remote=True)

            insert_job(
                cursor, conn,
                title=title,
                description=description[:5000] if description else "See job URL for full description.",
                company_id=company_id,
                source_id=source_id,
                location_id=location_id,
                source_url=source_url,
                job_type=job_type,
                work_mode='remote',
                salary_min=salary_min,
                salary_max=salary_max
            )
            jobs_inserted += 1

        except Exception as e:
            print(f"  Error processing Remotive job: {e}")
            jobs_skipped += 1
            continue

    cursor.close()
    conn.close()

    print(f"\nRemotive done.")
    print(f"  Jobs inserted : {jobs_inserted}")
    print(f"  Jobs skipped  : {jobs_skipped}")


# ═══════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 50)
    print("  Job Intelligence Platform — Scraper")
    print("=" * 50)

    # Run both scrapers
    scrape_remotive()       # API first — fast and no browser needed
    scrape_weworkremotely() # Browser scraper second

    print("\n" + "=" * 50)
    print("  All scraping complete.")
    print("=" * 50)