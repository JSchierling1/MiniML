import streamlit as st

BASE_URL = "http://127.0.0.1:5000"

#Import pages 
home_page = st.Page("pages/home.py", title="Home", icon="🏠")
details_page = st.Page("pages/details.py", title="Details", icon="🔍")
compare_page = st.Page("pages/compare.py", title="Compare", icon="⚖️")
running_page = st.Page("pages/running.py", title="Running", icon="🚀")
upload_page = st.Page("pages/upload.py", title="Upload", icon="📤")

#Navigation
pg = st.navigation([home_page, details_page, compare_page, running_page, upload_page])

pg.run()