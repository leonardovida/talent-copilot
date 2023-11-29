from typing import List

import requests
import streamlit as st

from cv_copilot.webapp.pdf_evaluation import display_recent_cvs, upload_pdf

API_ENDPOINT = "http://localhost:8000/api/job-descriptions"


def get_job_descriptions(limit: int) -> List[str]:
    """Get the most recent job descriptions from the API.

    :param limit: The number of job descriptions to return.
    :return: List of job descriptions.
    """
    response = requests.get(
        f"{API_ENDPOINT}/",
        params={"limit": limit},
        timeout=3,
    )
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch job descriptions")
        return []


def display_job_descriptions() -> None:
    """Display the job descriptions."""

    def toggle_add_job_form():
        st.session_state["add_job"] = not st.session_state.get("add_job", False)

    # Initialize the session state key for the form display state
    if "add_job" not in st.session_state:
        st.session_state["add_job"] = False

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Add new job")
    # Create the button and pass the callback function
    st.button("Add new job listing", on_click=toggle_add_job_form)

    # Check if the session state indicates the form should be displayed
    if st.session_state["add_job"]:
        with st.form("new_job_form"):
            new_job_title = st.text_input("Job Title", key="new_job_title")
            new_job_description = st.text_area(
                "Job Description",
                key="new_job_description",
            )
            submitted = st.form_submit_button("Submit")
            if submitted:
                with st.spinner("Creating the job description..."):
                    response = requests.post(
                        API_ENDPOINT,
                        json={
                            "title": new_job_title,
                            "description": new_job_description,
                        },
                        timeout=10,
                    )
                    if response.status_code == 200:
                        st.success("New job description added!")
                        st.session_state["add_job"] = False
                    else:
                        st.error("Failed to add job description")
                        print(response.text)

    # SUBHEADER
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("Job Descriptions")

    # LIST OF JOB DESCRIPTIONS
    job_descriptions = get_job_descriptions(limit=10)
    for job in job_descriptions:
        expander_key = f"expander_{job['id']}"
        is_expander_open = st.session_state.get(expander_key, False)

        with st.expander(f"{job['title']}", expanded=is_expander_open):
            # Use session state to track edit mode
            edit_key = f"edit_{job['id']}"
            if st.session_state.get(edit_key, False):
                # Display inputs for editing title and description
                edited_title = st.text_input(
                    "Job Title",
                    value=job["title"],
                    key=f"title_{job['id']}",
                )
                edited_description = st.text_area(
                    "Job Description",
                    value=job["description"],
                    key=f"description_{job['id']}",
                )
                if st.button("Save Changes", key=f"save_{job['id']}"):
                    response = requests.put(
                        f"{API_ENDPOINT}/{job['id']}/",
                        json={
                            "title": edited_title,
                            "description": edited_description,
                        },
                        timeout=10,
                    )
                    if response.status_code == 200:
                        st.success("Job description updated!")
                        # Reset the edit state and close the expander
                        st.session_state[edit_key] = False
                        st.session_state[expander_key] = False
                    else:
                        st.error(
                            f"Failed to update job description: {response.status_code}, {response.text}",
                        )
                        # Keep the expander open
                        st.session_state[expander_key] = True
            else:
                # Display job description as text
                st.text(job["description"])
                if st.button("Edit job description", key=f"edit_{job['id']}"):
                    # Enter edit mode and open the expander
                    st.session_state[edit_key] = True
                    st.session_state[expander_key] = True

            st.markdown("<br>", unsafe_allow_html=True)
            upload_pdf(job["id"])

            st.markdown("<br>", unsafe_allow_html=True)
            display_recent_cvs(job["id"], limit=10)
