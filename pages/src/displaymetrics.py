import streamlit as st
import requests
import pandas as pd

def display_metrics(metrics_details, key_prefix):
    st.write("### Metrics")
    st.write("#### Average Precision")
    # Dropdown for AP
    display_option_ap = st.selectbox(
        "Select display option for AP metrics",
        options=["Bar Chart", "DataFrame"],
        key=f"{key_prefix}_ap"
    )

    ap_df = pd.DataFrame([{
        "AP": metrics_details["ap"],
        "AP50": metrics_details["ap50"],
        "AP75": metrics_details["ap75"],
        "APS": metrics_details["aps"],
        "APM": metrics_details["apm"],
        "APL": metrics_details["apl"]
    }])

    # Display AP
    if display_option_ap == "Bar Chart":
        st.bar_chart(ap_df.T.rename(columns={0: "Value"}))
    else:
        st.dataframe(ap_df)

    st.write("#### Losses")
    
    # Dropdown Loss
    display_option_loss = st.selectbox(
        "Select display option for Loss metrics",
        options=["Bar Chart", "DataFrame"],
        key=f"{key_prefix}_loss"
    )
    
    losses_df = pd.DataFrame([{
        "Total Loss": metrics_details["total_loss"],
        "Classification Loss": metrics_details["loss_cls"],
        "Bbox Regression Loss": metrics_details["loss_box_reg"],
        "RPN Classification Loss": metrics_details["loss_rpn_cls"],
        "RPN Localization Loss": metrics_details["loss_rpn_loc"],
        "Mask Loss": metrics_details.get("mask_loss", "N/A")
    }])
    
    # Display Loss
    if display_option_loss == "Bar Chart":
        st.bar_chart(losses_df.T.rename(columns={0: "Value"}))
    else:
        st.dataframe(losses_df)