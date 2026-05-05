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
        response = requests.get(
            FULL_URL, params=params, timeout=10
        )  # params->It’s a dictionary that gets added to the URL as ?key=value e.g location=isb
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
page = st.sidebar.radio(
    label="Navigate to",
    options=["Job Browser", "Skill Matcher", "My Applications", "Analytics"],
)

st.sidebar.divider()
st.sidebar.subheader("Your Profile")

user_id = st.sidebar.number_input(
    label="Enter your User ID", min_value=1, value=1, step=1
)
st.sidebar.caption("Change User id to see different profiles")

# Job Browser Page
if page == "Job Browser":
    st.title("Job Browser")
    st.markdown("Browse all active job postings collected by the scraper.")

    jobs = fetch_api("/jobs")

    if not jobs:
        st.error("No jobs found,Run the scraper first to collect jobs.")

    else:
        df = pd.DataFrame(jobs)

        if not df.empty:
            # Reorder columns
            df = df[
                [
                    "job_id",
                    "title",
                    "company_name",
                    "work_mode",
                    "job_type",
                    "salary_min",
                    "salary_max",
                    "currency",
                    "city",
                    "country",
                    "posted_date",
                ]
            ]

            # Filters UI
            col1, col2, col3 = st.columns(3)

            with col1:
                filter_work_mode = st.selectbox(
                    label="Work Mode",
                    options=["All", "remote", "onsite", "hybrid"],
                )

            with col2:
                filter_job_type = st.selectbox(
                    label="Job Type",
                    options=["All", "full_time", "part_time", "contract", "internship"],
                )

            with col3:
                search_text = st.text_input("Search by title or company")

            # Apply filters

            if filter_work_mode != "All":
                df = df[df["work_mode"] == filter_work_mode]

            if filter_job_type != "All":
                df = df[df["job_type"] == filter_job_type]

            if search_text:
                df = df[
                    df["title"].str.contains(search_text, case=False, na=False)
                    | df["company_name"].str.contains(
                        search_text, case=False, na=False
                    )
                ]

            st.markdown(f"Showing {len(df)} jobs")

            st.dataframe(df, use_container_width=True)


# Skill Matcher Page
elif page == "Skill Matcher":
    st.title("Skill Matcher")
    st.markdown("Jobs are ranked Using JOINS (skill overlape)")

    user_data = fetch_api(f"/user/{user_id}")

    if not user_data:
        st.warning("No user found")

    else:
        if "full_name" in user_data:
            st.success(
                f"Logged in as: {user_data['full_name']} — {user_data['years_experience']} years experience"
            )

        st.subheader("Your Skills")

        if "skills" in user_data and len(user_data["skills"]) > 0:
            st.dataframe(
                pd.DataFrame(user_data["skills"]), use_container_width=True
            )
        else:
            st.info("You have no skills added yet. Add skills to get job matches.")

        st.subheader("Matched Jobs — Ranked by Skill Fit")

        matched_jobs = fetch_api(f"/jobs/match/{user_id}")

        if not matched_jobs:
            st.info("No matches found.")

        else:
            df_match = pd.DataFrame(matched_jobs)

            if "match_percent" in df_match.columns:
                df_match["match_percent"] = df_match["match_percent"].fillna(0)

                for _, row in df_match.iterrows():
                    st.write(row["title"])
                    st.progress(int(row["match_percent"]))

            st.dataframe(
                df_match[
                    [
                        "title",
                        "company_name",
                        "work_mode",
                        "total_required",
                        "matched_skills",
                        "match_percent",
                    ]
                ],
                use_container_width=True,
            )

        st.subheader("Apply to a Job")

        apply_job_id = st.number_input("Please Enter Job ID", min_value=1)
        cover_note = st.text_input("Please Enter Cover Note (Optional)")

        if st.button("Apply Now"):
            payload = {
                "user_id": user_id,
                "job_id": apply_job_id,
                "cover_note": cover_note,
            }

            response = requests.post(BASE_URL + "/jobs/apply", json=payload)

            if response.status_code != 200:
                st.error("Something went wrong")
            else:
                st.success("Successfully applied")

# My Applications Page
elif page == "My Applications":

    st.title("My Applications")
    st.markdown("Track the status of every job you have applied to.")

    apps = fetch_api(f"/applications/{user_id}")

    if not apps:
        st.info("You have not applied to any jobs yet.")
        st.markdown("Use the Skill Matcher page to find and apply to jobs.")
    else:
        df_apps = pd.DataFrame(apps)

        st.metric(label="Total Applications", value=len(df_apps))

        st.dataframe(
            df_apps[
                ["title", "company_name", "applied_at", "status", "match_score"]
            ],
            use_container_width=True,
        )

    st.subheader("Update Application Status")

    update_app_id = st.number_input("Application ID", min_value=1)

    new_status = st.selectbox(
        label="New Status",
        options=["submitted", "interviewing", "offered", "rejected", "withdrawn"],
    )

    if st.button("Update Status"):
        response = requests.patch(
            BASE_URL + f"/applications/{update_app_id}/status",
            params={"status": new_status},
        )

        if response.status_code == 200:
            st.success("Status updated successfully.")
            st.rerun()
        else:
            st.error("Error updating status")


# Analytics Page
elif page == "Analytics":

    st.title("Analytics")
    st.markdown("Visual insights from the job database.")

    all_jobs = fetch_api("/jobs")

    if not all_jobs:
        st.warning("No data available for analytics.")
    else:
        df_all = pd.DataFrame(all_jobs)

        if df_all.empty:
            st.warning("No job data found.")
        else:

            # Summary Metrics
            metric_col1, metric_col2, metric_col3 = st.columns(3)

            with metric_col1:
                st.metric("Total Active Jobs", len(df_all))

            with metric_col2:
                st.metric("Total Companies", df_all["company_name"].nunique())

            with metric_col3:
                st.metric("Data Sources", 2)

            # -------------------
            # Chart 1: Industry
            # -------------------
            st.subheader("Jobs by Industry")

            df_industry = df_all.groupby("industry")["job_id"].count().reset_index()
            df_industry.columns = ["industry", "count"]

            fig1 = px.bar(
                df_industry,
                x="industry",
                y="count",
                title="Number of Active Jobs per Industry",
                color="industry",
            )

            st.plotly_chart(fig1, use_container_width=True)

            # -------------------
            # Chart 2: Work Mode
            # -------------------
            st.subheader("Jobs by Work Mode")

            df_workmode = df_all.groupby("work_mode")["job_id"].count().reset_index()
            df_workmode.columns = ["work_mode", "count"]

            fig2 = px.pie(
                df_workmode,
                values="count",
                names="work_mode",
                title="Remote vs Onsite vs Hybrid",
                hole=0.4,
            )

            st.plotly_chart(fig2, use_container_width=True)

            # -------------------
            # Chart 3: Salary
            # -------------------
            st.subheader("Salary Distribution")

            df_salary = df_all[df_all["salary_max"].notna()]

            if not df_salary.empty:

                fig3 = px.histogram(
                    df_salary,
                    x="salary_max",
                    nbins=20,
                    title="Distribution of Maximum Salaries (USD)",
                    labels={
                        "salary_max": "Maximum Salary",
                        "count": "Number of Jobs",
                    },
                )

                st.plotly_chart(fig3, use_container_width=True)

            else:
                st.info(
                    "Not enough salary data to display. Most scraped jobs do not include salary."
                )