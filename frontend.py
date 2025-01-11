import streamlit as st
import requests
import pandas as pd 
import numpy as np

from frontend_details_page import show_details_page 

BASE_URL = "http://127.0.0.1:5000"

st.title("MiniML - The Machine Learning Training Tracker")

#Sidebar 
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Details", "New Experiment"])

# Home Page 
if page == "Home": 
    st.write("### Overview of all Experiments")
    response = requests.get(f"{BASE_URL}/experiments")
    if response.status_code == 200: 
        experiments = pd.DataFrame(response.json())
        st.table(experiments)
    else: 
        st.error("Failed to load data.")
        
# Details Page 
elif page == "Details": 
    show_details_page()
