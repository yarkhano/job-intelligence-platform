# You do not write HTML or CSS. You write Python and Streamlit converts it into a web page automatically.

import streamlit as st
import requests  # use this to call your FastAPI backend endpoints dashboard sends a request to http://localhost:8000
import pandas as pd  # to show clean data of tables
import plotly.express as px  # For analytics

BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Job Intelligence Platform",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)


def fetch_api(endpoint: str, params: dict = None):
    try:
        FULL_URL = f"{BASE_URL}{endpoint}"
        response = requests.get(FULL_URL, params=params,
                                timeout=10)  # params->It’s a dictionary that gets added to the URL as ?key=value e.g location=isb
        response.raise_for_status()  # it checks status (200,400) if 200 ok, otherwise throw error
        return response.json()

    except requests.exceptions.ConnectionError:
        st.error("connection error")

    except Exception as e:
        st.error(str(e))


# Create the left sidebar where users click to switch between pages.
st.sidebar.title("JIP Dashboard")
st.sidebar.markdown("Job Intelligence Platform")
st.sidebar.divider()

# Navigation Menu
page = st.sidebar.radio(label="Navigate to", options=["Job Browser", "Skill Matcher", "My Applications", "Analytics"])

st.sidebar.divider()
st.sidebar.subheader("Your Profile")

user_id = st.sidebar.number_input(label="Enter your User ID", min_value=1, value=1, step=1)
st.sidebar.caption("Change User id to see different profiles")

if page == "Job Browser":
    st.title("Job Browser")
    st.markdown("Browse all active job postings collected by the scraper.")

    jobs = fetch_api("/jobs")

    if jobs is None:
        st.error("No jobs found,Run the scraper first to collect jobs.")

    df = pd.DataFrame(jobs)

    if df.empty:
        st.warning("No jobs in database.")

    # Reorder columns
    df = df[[
        "job_id", "title", "company_name", "work_mode", "job_type",
        "salary_min", "salary_max", "currency", "city", "country", "posted_date"
    ]]

    # Filters UI
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_work_mode = st.selectbox(label="Work Mode", options=["All", "remote", "onsite", "hybrid"])

    with col2:
        filter_job_type = st.selectbox(label="Job Type",
                                       options=["All", "full_time", "part_time", "contract", "internship"])

    with col3:
        search_text = st.text_input("Search by title or company")

    # Apply filters

    # Work Mode filter
    if filter_work_mode != "All":
        df = df[df["work_mode"] == filter_work_mode]

    # Job Type filter
    if filter_job_type != "All":
        df = df[df["job_type"] == filter_job_type]

    # Search filter (title OR company_name)
    if search_text:
        df = df[
            df["title"].str.contains(search_text, case=False, na=False) |
            df["company_name"].str.contains(search_text, case=False, na=False)
            ]

    # Show number of jobs
    st.markdown(f"Showing {len(df)} jobs")

    # Display table
    st.dataframe(df, use_container_width=True))