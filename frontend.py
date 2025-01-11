import streamlit as st
import requests
import pandas as pd 
import numpy as np

from frontend_details_page import show_details_page 
from frontend_home_page import show_home_page
from frontend_running_page import show_running_page
from frontend_compare_page import show_compare_page

BASE_URL = "http://127.0.0.1:5000"

st.set_page_config(layout="wide")
st.title("MiniML - The Machine Learning Training Tracker")
col1, col2, col3 = st.columns(3)

#Sidebar 
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Details", "Currently Running", "Compare"])

# Home Page 
if page == "Home": 
    show_home_page()
        
# Details Page 
elif page == "Details":
    with col2: 
        show_details_page()

elif page == "Currently Running": 
    show_running_page()
    
elif page == "Compare":
    show_compare_page()