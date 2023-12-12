from datetime import datetime
from typing import Dict, List

import requests
import streamlit as st

API_ENDPOINT = "http://localhost:8000/api/pdfs"
PARSED_TEXT_API_ENDPOINT = "http://localhost:8000/api/parsed-texts"
API_SCORE_ENDPOINT = "http://localhost:8000/api/scores"


def upload_pdf(job_id: str) -> None:
    """Upload a PDF to the database.

    :param job_id: The ID of the job description to upload the PDF to.
    """
    pdf_file = st.file_uploader(
        "Drag and drop your CV here",
        type=["pdf"],
        key=f"file_uploader_{job_id}",
        # accept_multiple_files=True, TODO: Need to add this functionality
    )
    if st.button("Upload", key=f"upload_button_{job_id}"):
        if pdf_file is not None:
            files = {
                "pdf_file": (pdf_file.name, pdf_file.getvalue(), "application/pdf"),
            }
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


def display_evaluation_by_category_and_type(
    skills_extract: Dict[str, Dict[str, List[str]]],
) -> None:
    """Display the evaluation of the CV by category and type.

    :param skills_extract: The skills extracted from the CV.
    """
    st.subheader("CV Evaluation")
    skills = skills_extract["parsed_skills"]
    for skill_category, skill_details in skills.items():
        if isinstance(skill_details, dict):
            st.markdown(f"### {skill_category}")
            for skill_type, skill_type_details in skill_details.items():
                if skill_type_details is not None:
                    st.markdown(f"#### {skill_type}")
                    # Create a list of dictionaries for each skill
                    table_data = [
                        {
                            "Skill Name": skill["name"],
                            "CV Match": skill["match"],
                            "Content Match": skill["content_match"],
                            "reasoning": skill["reasoning"],
                        }
                        for skill_name, skill in skill_type_details.items()
                        if skill is not None
                    ]
                    # Display the table in Streamlit
                    st.table(table_data)


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
    else:
        st.error(f"Failed to evaluate CV - {response.status_code}, {response.text}")


def process_cv_score(job_id: str, cv_id: str) -> float | str:
    """Process a CV Score.

    :param job_id: The ID of the job description to process the CV for.
    :param cv_id: The ID of the CV to process.
    """
    params = {"job_id": job_id, "pdf_id": cv_id}
    response = requests.post(
        f"{API_SCORE_ENDPOINT}/process/{cv_id}/{job_id}",
        timeout=600,
        params=params,
    )
    if response.status_code == 200:
        st.success("Score generated!")
        return round(response.json()["score"], 2)
    else:
        st.error(
            f"Failed to generate CV Score - {response.status_code}, {response.text}",
        )
        return "Undefined"


def get_last_cv_score(job_id: str, cv_id: str) -> float | str:
    """Get last CV Score.

    :param job_id: The ID of the job description to process the CV for.
    :param cv_id: The ID of the CV to process.
    """
    params = {"job_id": job_id, "pdf_id": cv_id}
    response = requests.get(
        f"{API_SCORE_ENDPOINT}/{cv_id}/{job_id}",
        timeout=600,
        params=params,
    )
    if response.status_code == 200:
        return round(response.json()["score"], 2)
    else:
        return "Undefined"


def delete_cv(cv_id: str) -> None:
    """Delete a CV.

    :param cv_id: The ID of the CV to delete.
    """
    response = requests.delete(f"{API_ENDPOINT}/{cv_id}", timeout=5)
    if response.status_code == 200:
        st.success("CV deleted!")
    else:
        st.error(f"Failed to delete CV - {response.status_code}, {response.text}")


def display_recent_cvs(job_id: str, limit: str = "10") -> None:
    """Display the most recent CVs.

    :param job_id: The ID of the job description to display the CVs for.
    :param limit: The number of CVs to display.
    """
    recent_cvs = get_cv_list(job_id, limit)

    for index, cv in enumerate(recent_cvs):
        col1, col2, col3, col4 = st.columns([2, 4, 1, 1])
        col1.text(cv["name"])

        try:
            score = get_last_cv_score(job_id, cv["id"])
        except:
            score = None

        with col2:
            with st.spinner("Fetching evaluation..."):
                fetch_key = f"fetch_evaluation_{cv['id']}"
                if st.button("Fetch evaluation", key=fetch_key):
                    response = requests.get(
                        f"{PARSED_TEXT_API_ENDPOINT}/{cv['id']}/",
                        timeout=3,
                    )
                    if response.status_code == 200:
                        display_evaluation_by_category_and_type(response.json())
                    else:
                        st.error(
                            f"Failed to fetch evaluation for CV {cv['id']}: {response.status_code}",
                        )

        with col3:
            with st.spinner("Evaluating..."):
                evaluate_key = f"evaluate_{cv['id']}"
                if st.button("Evaluate CV", key=evaluate_key):
                    process_cv(job_id, cv["id"])

            score_key = f"score_calculate_{cv['id']}"
            if st.button("Generate CV Score", key=score_key):
                score = process_cv_score(job_id, cv["id"])

            delete_key = f"delete_cv_{cv['id']}"
            if st.button("Delete CV", key=delete_key):
                delete_cv(cv["id"])

        with col4:
            if score:
                st.markdown(f"#### Score: {score}")

        st.markdown("<hr>", unsafe_allow_html=True)
