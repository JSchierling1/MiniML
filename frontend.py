import streamlit as st
import requests
import pandas as pd 
import numpy as np

from pages.details import show_details_page 
from pages.home import show_home_page
from pages.running import show_running_page
from pages.compare import show_compare_page

BASE_URL = "http://127.0.0.1:5000"

#Import pages 
home_page = st.Page("pages/home.py", title="Home", icon="🏠")
details_page = st.Page("pages/details.py", title="Details", icon="🔍")
compare_page = st.Page("pages/compare.py", title="Compare", icon="⚖️")
running_page = st.Page("pages/running.py", title="Running", icon="🚀")

#Navigation
pg = st.navigation([home_page, details_page, compare_page, running_page])

pg.run()