import streamlit as st
import requests

BASE_URL = "http://localhost:5000"

st.title("MiniML Experiment Tracker")

# Liste aller Experimente abrufen
response = requests.get(f"{BASE_URL}/experiments")
if response.status_code == 200:
    experiments = response.json()
    st.write("### Alle Experimente")
    st.table(experiments)
else:
    st.error("Fehler beim Abrufen der Experimente.")
