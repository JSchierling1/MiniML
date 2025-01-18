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

    # Upload and parse log
    with st.spinner("Uploading and parsing log..."):
        response = requests.post(f"{BASE_URL}/experiments/parse-log", files={"file": uploaded_file})
    
    if response.status_code == 200:
        # Parsing successful
        parsed_data = response.json()
        st.success("Log file uploaded and parsed successfully!")

        # Show data preview
        st.write("### Extracted Data")
        st.json(parsed_data) 

        # Optional: Convert to DataFrame for better viewing
        df = pd.DataFrame([parsed_data])
        st.dataframe(df)

        # Input for Run ID
        run_id = st.text_input("Enter a name for your run (run_id):")

        # Confirm and Save
        if run_id and st.button("Confirm and Save Run"):
            #Add missing data
            parsed_data["dataset"] = parsed_data.get("dataset", "unknown_dataset")
            parsed_data["model"] = parsed_data.get("model", "unknown_model")
            parsed_data["num_epochs"] = parsed_data.get("num_epochs", 0)
            with st.spinner("Saving run..."):
                save_response = requests.post(
                    f"{BASE_URL}/experiments/upload-run",
                    json={"run_id": run_id, **parsed_data}
                )
            
            if save_response.status_code == 201:
                st.success(f"Run '{run_id}' saved successfully!")
            else:
                st.error(f"Failed to save run '{run_id}': {save_response.text}")
    else:
        st.error(f"Failed to upload log file: {response.text}")
