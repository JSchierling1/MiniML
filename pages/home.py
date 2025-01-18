import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://localhost:5000"
st.set_page_config(page_title="MiniML: Home", layout="wide")
st.title("MiniML: A Minimalistic ML Experiment Tracking Tool")

st.write("### Overview of all Experiments")
response = requests.get(f"{BASE_URL}/experiments")
if response.status_code == 200: 
    experiments = pd.DataFrame(response.json())
    columns_order = [
        "id",
        "run_id", 
        "dataset", 
        "started_at",
        "status",
        "model",
        "learning_rate",
        "batch_size",
        "num_epochs",
        "ap",
        "ap50",
        "ap75",
        "aps",
        "apm",
        "apl",
        "total_loss",
        "loss_cls",
        "loss_box_reg",
        "loss_rpn_cls",
        "loss_rpn_loc",
        "iterations",
        "mask_loss"
    ]
    experiments = experiments[columns_order]
    experiments = experiments.rename(columns={
        "id": "ID",
        "run_id": "Run ID",
        "dataset": "Dataset",
        "started_at": "Started At",
        "status": "Status",
        "model": "Model",
        "learning_rate": "Learning Rate",
        "batch_size": "Batch Size",
        "num_epochs": "Number of Epochs",
        "ap": "AP",
        "ap50": "AP50",
        "ap75": "AP75",
        "aps": "APS",
        "apm": "APM",
        "apl": "APL",
        "total_loss": "Total Loss",
        "loss_cls": "Classification Loss",
        "loss_box_reg": "Bbox Regression Loss",
        "loss_rpn_cls": "RPN Classification Loss",
        "loss_rpn_loc": "RPN Localization Loss",
        "iterations": "Iterations",
        "mask_loss": "Mask Loss"
    })
    st.dataframe(experiments)
else: 
    st.error("Failed to load data.")