import streamlit as st
import requests
import pandas as pd
from pages.src.displaymetrics import display_metrics

BASE_URL = "http://localhost:5000"

st.set_page_config(page_title="MiniML: Details", layout="wide")
st.title("Details of a Run")

# Get Run IDs
response = requests.get(f"{BASE_URL}/experiments")
if response.status_code == 200: 
    experiments = response.json()
    run_ids = [exp["run_id"] for exp in experiments]
else:
    st.error("Failed to load run IDs")
    st.stop()

# Dropdown to select Run
selected_run_id = st.selectbox("Select a Run ID", options=run_ids, key="run_id")

if selected_run_id:
    run_response_metrics = requests.get(f"{BASE_URL}/experiments/{selected_run_id}/metrics")
    run_response_status = requests.get(f"{BASE_URL}/experiments/{selected_run_id}/status")
    run_response_info = requests.get(f"{BASE_URL}/experiments/{selected_run_id}/info")
    
    if run_response_status.status_code == 200 and run_response_info.status_code == 200:
        status_details = run_response_status.json()
        info_details = run_response_info.json()
        
        st.write(f"### Details for Run ID: {selected_run_id}")

        # Display Run Information
        st.write("#### Run Information")
        st.dataframe({
            "Dataset": info_details["dataset"],
            "Model": info_details["model"], 
            "Status": status_details["status"],
            "Started At": status_details["started_at"]
        })
        
        # Display Hyperparameters
        st.write("#### Hyperparameters")
        hyper_df = pd.DataFrame([{
            "Learning Rate": info_details["learning_rate"],
            "Batch Size": info_details["batch_size"],
            "Number of Epochs": info_details["num_epochs"]
        }])
        st.dataframe(hyper_df)

    if run_response_metrics.status_code == 200: 
        metric_details = run_response_metrics.json()    

        # Display Metrics
        display_metrics(metric_details, key_prefix="details")
    else:
        st.error("Failed to load Metrics.")
