from io import StringIO
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="MiniML: Upload Logs", layout="wide")
st.title("Upload Logs")

BASE_URL = "http://localhost:5000"

st.write("### Upload your Log file to create a new run")

# File Upload
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # Parse file content
    string_data = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    
    # Show log content preview
    st.write("### Log File Content Preview")
    st.text_area("Log Preview", string_data, height=200)

    # Upload to backend
    with st.spinner("Uploading log..."):
        response = requests.post(f"{BASE_URL}/experiments", files={"file": uploaded_file})
    
    if response.status_code == 201:
        st.success("Upload successful! Please name your run.")
        
        # Input for Run ID
        run_id = st.text_input("Enter a name for your run (run_id):")
        
        if run_id: 
            with st.spinner("Uploading and parsing log..."):
                response = requests.post(f"{BASE_URL}/parse-log", files={"file": uploaded_file})
        
            if response.status_code == 200:
                parsed_data = response.json()
                
                experiments = pd.DataFrame([parsed_data])
                
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
                "mask_loss",
            ]
            experiments = experiments[columns_order]
            experiments = experiments.rename(
                columns={
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
                    "mask_loss": "Mask Loss",
                }
            )
            
            # Show data preview
            st.write("### Data Preview")
            st.dataframe(experiments)
        
        #Confirm and Save
        if st.button("Confirm and Save Run"):
            with st.spinner("Saving run..."):
                save_response = requests.post(
                    f"{BASE_URL}/create-run",
                    json={"run_id": run_id, **parsed_data}
                )
            
            if save_response.status_code == 201:
                st.success(f"Run '{run_id}' saved successfully!")
            else:
                st.error(f"Failed to save run '{run_id}': {save_response.text}")
    else:
        st.error(f"Failed to upload log file: {response.text}")
