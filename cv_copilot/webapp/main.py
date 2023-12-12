import streamlit as st
from job_descriptions import display_job_descriptions

# Main page setup
st.set_page_config(page_title="CV-Copilot", page_icon="🤖", layout="wide")
st.title("CV-Copilot")

st.markdown("<br><br>", unsafe_allow_html=True)

# Display job descriptions with PDF upload and evaluation
display_job_descriptions()
