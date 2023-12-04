from datetime import datetime
from typing import Dict, List

import requests
import streamlit as st

API_ENDPOINT = "http://localhost:8000/api/pdfs"


def upload_pdf(job_id: str) -> None:
    """Upload a PDF to the database.

    :param job_id: The ID of the job description to upload the PDF to.
    """
    pdf_file = st.file_uploader(
        "Drag and drop your CV here",
        type=["pdf"],
        key=f"file_uploader_{job_id}",
    )
    if st.button("Upload", key=f"upload_button_{job_id}"):
        if pdf_file is not None:
            files = {"pdf_file": (pdf_file.name, pdf_file, "application/pdf")}
            data = {
                "name": pdf_file.name,
                "job_id": job_id,
                "created_date": str(datetime.now()),
            }
            response = requests.post(API_ENDPOINT, files=files, data=data, timeout=5)
            if 200 <= response.status_code < 300:
                st.success("CV uploaded")
            else:
                st.error(
                    f"Failed to upload CV: {response.status_code} - {response}",
                )
        else:
            st.error("Error. Please upload a CV in PDF format.")


def get_cv_list(job_id: str, limit: str) -> List[Dict[str, str]]:
    """Get the list of CVs for a job description.

    :param job_id: The ID of the job description to get the CVs for.
    :return: List of CVs.
    """
    params = {"job_id": job_id, "limit": limit}
    response = requests.get(
        f"{API_ENDPOINT}",
        timeout=10,
        params=params,
    )
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch CVs: {response.status_code}, {response.text}")
        return []


def process_cv(job_id: str, cv_id: str) -> None:
    """Process a CV.

    :param job_id: The ID of the job description to process the CV for.
    :param cv_id: The ID of the CV to process.
    """
    params = {"job_id": job_id, "pdf_id": cv_id}
    response = requests.get(
        f"{API_ENDPOINT}/{cv_id}/process",
        timeout=600,
        params=params,
    )
    if response.status_code == 200:
        st.success("CV evaluated!")
        st.write(response.json())
    else:
        st.error(f"Failed to evaluate CV - {response.status_code}, {response.text}")


def delete_cv(cv_id: str) -> None:
    """Delete a CV.

    :param cv_id: The ID of the CV to delete.
    """
    response = requests.delete(f"{API_ENDPOINT}/{cv_id}", timeout=5)
    if response.status_code == 200:
        st.success("CV deleted!")
    else:
        st.error(f"Failed to delete CV - {response.status_code}, {response.text}")


def display_recent_cvs(job_id: str, limit: str = "10"):
    """Display the most recent CVs.

    :param job_id: The ID of the job description to display the CVs for.
    :param limit: The number of CVs to display.
    """
    recent_cvs = get_cv_list(job_id, limit)

    for index, cv in enumerate(recent_cvs):
        col1, col2, col3 = st.columns([8, 1, 1])
        col1.text(cv["name"])

        with col2:
            with st.spinner("Evaluating..."):
                evaluate_key = f"evaluate_{cv['id']}"
                if st.button("Evaluate CV", key=evaluate_key):
                    process_cv(job_id, cv["id"])

        with col3:
            delete_key = f"delete_cv_{cv['id']}"
            if st.button("Delete CV", key=delete_key):
                delete_cv(cv["id"])
