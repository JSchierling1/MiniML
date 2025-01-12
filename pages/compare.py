import streamlit as st
import requests
import pandas as pd
from pages.details import run_ids
from pages.src.displaymetrics import display_metrics

BASE_URL = "http://localhost:5000"

st.set_page_config(page_title="MiniML: Compare", layout="wide")
st.title("Compare Runs")

col1, col2 = st.columns(2)

def get_run_details(run_id):
    info_response = requests.get(f"{BASE_URL}/experiments/{run_id}/info")
    status_response = requests.get(f"{BASE_URL}/experiments/{run_id}/status")
    metrics_response = requests.get(f"{BASE_URL}/experiments/{run_id}/metrics")

    if info_response.status_code == 200 and status_response.status_code == 200 and metrics_response.status_code == 200:
        return {
            "info": info_response.json(),
            "status": status_response.json(),
            "metrics": metrics_response.json()
        }
    else:
        st.error(f"Failed to load data for Run ID: {run_id}")
        return None

# Get all available run IDs
response = requests.get(f"{BASE_URL}/experiments")
if response.status_code == 200:
    experiments = response.json()
    run_ids = [exp["run_id"] for exp in experiments]
else:
    st.error("Failed to load run IDs")
    st.stop()
    

# Column for first run to compare
with col1:
    st.write("### Run 1")
    selected_run_id_1 = st.selectbox("Select a Run ID", options=run_ids, key="run_1")

    if selected_run_id_1:
        run_1_details = get_run_details(selected_run_id_1)
        if run_1_details:
            info_details_1 = run_1_details["info"]
            status_details_1 = run_1_details["status"]
            metrics_details_1 = run_1_details["metrics"]

            st.write("#### Run Information")
            st.dataframe({
                "Dataset": info_details_1["dataset"],
                "Model": info_details_1["model"], 
                "Status": status_details_1["status"],
                "Started At": status_details_1["started_at"]
            })

            st.write("#### Hyperparameters")
            hyper_df_1 = pd.DataFrame([{
                "Learning Rate": info_details_1["learning_rate"],
                "Batch Size": info_details_1["batch_size"],
                "Number of Epochs": info_details_1["num_epochs"]
            }])
            st.dataframe(hyper_df_1)

            display_metrics(metrics_details_1, key_prefix="run_1")
        
# Column for second run to compare
with col2:
    st.write("### Run 2")
    selected_run_id_2 = st.selectbox("Select a Run ID", options=run_ids, key="run_2")

    if selected_run_id_2:
        run_2_details = get_run_details(selected_run_id_2)
        if run_2_details:
            info_details_2 = run_2_details["info"]
            status_details_2 = run_2_details["status"]
            metrics_details_2 = run_2_details["metrics"]

            st.write("#### Run Information")
            st.dataframe({
                "Dataset": info_details_2["dataset"],
                "Model": info_details_2["model"], 
                "Status": status_details_2["status"],
                "Started At": status_details_2["started_at"]
            })

            st.write("#### Hyperparameters")
            hyper_df_2 = pd.DataFrame([{
                "Learning Rate": info_details_2["learning_rate"],
                "Batch Size": info_details_2["batch_size"],
                "Number of Epochs": info_details_2["num_epochs"]
            }])
            st.dataframe(hyper_df_2)

            display_metrics(metrics_details_2, key_prefix="run_2")
            
# Compare metrics
if run_1_details and run_2_details: 
    st.write("### Comparison")
    
    #Dropdown to select metric
    metric_type = st.selectbox(
        "Select metric type to compare", 
        options=["AP", "Loss"]
    )
    
    if metric_type == "AP":
        comparison_df = pd.DataFrame({
            "Metric": ["AP", "AP50", "AP75", "APS", "APM", "APL"],
            f"Run {selected_run_id_1}": [
                metrics_details_1["ap"],
                metrics_details_1["ap50"],
                metrics_details_1["ap75"],
                metrics_details_1["aps"],
                metrics_details_1["apm"],
                metrics_details_1["apl"]
            ],
            f"Run {selected_run_id_2}": [
                metrics_details_2["ap"],
                metrics_details_2["ap50"],
                metrics_details_2["ap75"],
                metrics_details_2["aps"],
                metrics_details_2["apm"],
                metrics_details_2["apl"]
            ]
        })
        st.write("#### AP Metrics Comparison")
        st.bar_chart(comparison_df.set_index("Metric"))
    
    elif metric_type == "Loss":
        comparison_df = pd.DataFrame({
            "Metric": ["Total Loss", "Classification Loss", "BBox Loss", "Mask Loss"],
            f"Run {selected_run_id_1}": [
                metrics_details_1["total_loss"],
                metrics_details_1["cls_loss"],
                metrics_details_1["bbox_loss"],
                metrics_details_1.get("mask_loss", "N/A")
            ],
            f"Run {selected_run_id_2}": [
                metrics_details_2["total_loss"],
                metrics_details_2["cls_loss"],
                metrics_details_2["bbox_loss"],
                metrics_details_2.get("mask_loss", "N/A")
            ]
        })
        st.write("#### Loss Metrics Comparison")
        st.bar_chart(comparison_df.set_index("Metric"))
    
