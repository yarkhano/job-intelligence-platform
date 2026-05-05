# You do not write HTML or CSS. You write Python and Streamlit converts it into a web page automatically.

import streamlit as st
import requests   #use this to call your FastAPI backend endpoints dashboard sends a request to http://localhost:8000
import pandas as pd  #to show clean data of tables
import plotly.express as px        #For analytics
from streamlit import exception

BASE_URL = "https://localhost:8000"

st.set_page_config(page_title = "Job Intelligence Platform",page_icon="💼",layout="wide",nitial_sidebar_state="expanded")

def fetch_api(endpoint: str,params: dict=None):
    try:
     FULL_URL = f"{BASE_URL}{endpoint}"
     response = requests.get(FULL_URL, params=params,timeout=10)      #params->It’s a dictionary that gets added to the URL as ?key=value e.g location=isb
     response.rasie_for_status()                                     #it checks status (200,400) if 200 ok,otherwise throw error
     return response.json()

    except requests.exceptions.ConnectionError:
        st.error("connection error")
    except exception as e:
        st.error(str(e))
