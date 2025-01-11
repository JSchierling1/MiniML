import streamlit as st
import requests
import pandas as pd 
import numpy as np 

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
    st.write("### Details of a Run")
    
    #Get Run IDs
    response = requests.get(f"{BASE_URL}/experiments")
    if response.status_code == 200: 
        experiments = response.json()
        run_ids = [exp["run_id"] for exp in experiments]
        
    #Dropdown
    selected_run_id = st.selectbox("Select a Run ID", options=run_ids)
    
    if selected_run_id:
        run_response_metrics = requests.get(f"{BASE_URL}/experiments/{selected_run_id}/metrics")
        run_response_status = requests.get(f"{BASE_URL}/experiments/{selected_run_id}/status")
        run_response_info = requests.get(f"{BASE_URL}/experiments/{selected_run_id}/info")
        
        if run_response_status.status_code == 200  & run_response_info.status_code == 200:
            status_details = run_response_status.json()
            info_details = run_response_info.json()
            
            st.write(f"### Details for Run ID: {selected_run_id}")

            st.write("#### Run Information")
            st.table({
                "Dataset": info_details["dataset"],
                "Model": info_details["model"], 
                "Status": status_details["status"],
                "Started At": status_details["started_at"]
            })
            
            st.write("#### Hyperparameters")
            hyper_df = pd.DataFrame([{
                "Learning Rate": info_details["learning_rate"],
                "Batch Size": info_details["batch_size"],
                "Number of Epochs": info_details["num_epochs"]
            }])
            st.table(hyper_df)
            
        if run_response_metrics.status_code == 200: 
            metric_details = run_response_metrics.json()    
            
            st.write("### Metrics")
            st.write("#### Average Precision")
            ap_df = pd.DataFrame([{
                "AP": metric_details["ap"],
                "AP50": metric_details["ap50"],
                "AP75": metric_details["ap75"],
                "APS": metric_details["aps"],
                "APM": metric_details["apm"],
                "APL": metric_details["apl"]
            }])
            st.table(ap_df)
            
            st.write("#### Losses")
            losses_df = pd.DataFrame([{
                    "Total Loss": metric_details["total_loss"],
                    "Classification Loss": metric_details["cls_loss"],
                    "Bbox Loss": metric_details["bbox_loss"],
                    "Mask Loss": metric_details.get("mask_loss", "N/A")
                }])
            st.table(losses_df)
        else:
                st.error("Failed to load Details.")
    else:
        st.error("Failed to load Runs.")
