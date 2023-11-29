from datetime import datetime

import requests
import streamlit as st

API_ENDPOINT = "http://localhost:8000/api/pdfs"


def evaluate_cv(pdf_id: int):
    """Evaluate a CV.

    :param pdf_id: The ID of the PDF to evaluate.
    """
    # Placeholder for the evaluation logic


def upload_pdf(job_id: int) -> None:
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
            # Create the files dictionary for the request
            files = {"pdf_file": (pdf_file.name, pdf_file, "application/pdf")}
            data = {
                "name": pdf_file.name,
                "job_id": job_id,
                "created_date": str(datetime.now()),
            }
            req = requests.Request("POST", f"{API_ENDPOINT}", files=files, data=data)
            prepared = req.prepare()
            response = requests.post(API_ENDPOINT, files=files, data=data, timeout=5)
            if 200 <= response.status_code < 300:
                st.success("CV uploaded")
            else:
                st.error(
                    f"Failed to upload CV: {response.status_code}. {prepared.body}",
                )
        else:
            st.error("Error. Please upload a CV in PDF format.")


def display_recent_cvs(job_id: int, limit: int = 10):
    params = {"job_id": job_id, "limit": limit}
    response = requests.get(
        f"{API_ENDPOINT}",
        timeout=10,
        params=params,
    )

    if response.status_code == 200:
        recent_cvs = response.json()

        for index, cv in enumerate(recent_cvs):
            col1, col2 = st.columns([4, 1])
            col1.text(cv["name"])

            if col2.button("Evaluate CV", key=f"evaluate_{cv['id']}"):
                print("Evaluating CV...")
    else:
        st.error(f"Failed to fetch recent CVs: {response.status_code}, {response.text}")
