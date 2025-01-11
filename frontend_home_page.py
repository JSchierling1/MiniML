import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://localhost:5000"

def show_home_page():
    st.write("### Overview of all Experiments")
    response = requests.get(f"{BASE_URL}/experiments")
    if response.status_code == 200: 
        experiments = pd.DataFrame(response.json())
        st.table(experiments)
    else: 
        st.error("Failed to load data.")