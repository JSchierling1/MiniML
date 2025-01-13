import streamlit as st
import requests
import pandas as pd
import time 

st.set_page_config(page_title="MiniML: Running", layout="wide")
st.title("Currently Running")

BASE_URL = "http://localhost:5000"

# Get Run IDs
response = requests.get(f"{BASE_URL}/experiments")
if response.status_code == 200: 
    experiments = response.json()
    run_ids = [exp["run_id"] for exp in experiments]
else:
    st.error("Failed to load run IDs")
    st.stop()
    
selected_run_id = st.selectbox("Select a Run ID", options=run_ids, key="run_id")
log_area = st.empty()

if selected_run_id:
    st.write('### Logs for Run ID:', selected_run_id)
    while True: 
        try: 
            response = requests.get(f'{BASE_URL}/experiments/{selected_run_id}/logs')
            if response.status_code == 200:
                log_area.text(response.text)
            else:
                st.error(f"Failed to load logs for Run ID: {selected_run_id}")
        except Exception as e:
            st.error(f"Error fetching logs: {e}")
        time.sleep(1)