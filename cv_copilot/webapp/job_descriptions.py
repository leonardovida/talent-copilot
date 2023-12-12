from typing import Dict, List, Optional

import requests
import streamlit as st

from cv_copilot.web.dto.job_description.schema import ParsedJobDescriptionDTO
from cv_copilot.webapp.pdf_evaluation import display_recent_cvs, upload_pdf

API_ENDPOINT = "http://localhost:8000/api/job-descriptions"
API_ENDPOINT_PARSED = "http://localhost:8000/api/parsed-job-descriptions"


def get_job_descriptions(limit: int) -> List[Dict[str, str]]:
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
    st.error("Failed to fetch job descriptions")
    return []


def get_parsed_job_description(
    job_description_id: str,
) -> Optional[ParsedJobDescriptionDTO]:
    response = requests.get(
        f"{API_ENDPOINT_PARSED}/{job_description_id}/",
        timeout=3,
    )
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch parsed job description: {response.status_code}")
        return None


def display_delete_job_description_button(job_id: str) -> None:
    """Display a button to delete the job description.

    :param job_id: The ID of the job description to delete.
    """
    if st.button("Delete job description", key=f"delete_job_{job_id}"):
        response = requests.delete(
            f"{API_ENDPOINT}/{job_id}/",
            timeout=10,
        )
        if response.status_code == 200:
            st.success("Job description deleted!")
            # Refresh page
            st.experimental_rerun()
        else:
            st.error(
                f"Failed to delete job description {job_id}: {response.status_code}, {response}",
            )


def display_skills_by_category_and_type(
    skills_extract: ParsedJobDescriptionDTO,
) -> None:
    """Display skills grouped by category and type.

    TODO: Parse the response using the pydantic model instead of a dict.

    :param skills_extract: The SkillsExtract object containing required and nice to have skills.
    """
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
                            "Description": skill["description"],
                            "Long Description": skill.get("long_description", ""),
                            "Skill Categories": ", ".join(
                                skill.get("skill_categories", []),
                            ),
                        }
                        for skill_name, skill in skill_type_details.items()
                        if skill is not None
                    ]
                    # Display the table in Streamlit
                    st.table(table_data)


def display_weights_sliders(job_id: int) -> None:
    """Display the sliders to adjust the weights for the skills."""
    col1, col2 = st.columns([1, 2])
    with col1:
        st.text("Required relative importance")
    with col2:
        st.slider(
            "Required relative importance",
            1,
            5,
            3,
            1,
            key=f"slider_required_{job_id}",
        )
    col1, col2 = st.columns([1, 2])

    with col1:
        st.text("Nice-to-have relative importance")
    with col2:
        st.slider(
            "Nice-to-have relative importance",
            1,
            5,
            3,
            1,
            key=f"slider_nice_to_have_{job_id}",
        )


def create_new_job_description_form() -> None:
    """Display the form to create a new job description."""
    # Check if the session state indicates the form should be displayed
    if st.session_state["add_job"]:
        with st.form("new_job_form"):
            new_job_title = st.text_input(
                "Job Title",
                key="new_job_title",
                placeholder="Paste the job title here...",
            )
            new_job_description = st.text_area(
                "Job Description",
                key="new_job_description",
                height=350,
                placeholder="Paste the job description here...",
            )
            submitted = st.form_submit_button("Submit")
            if submitted:
                with st.spinner("Parsing the job description..."):
                    response = requests.post(
                        API_ENDPOINT,
                        json={
                            "title": new_job_title,
                            "description": new_job_description,
                        },
                        timeout=3,
                    )
                    if response.status_code == 200:
                        st.success("New job description added!")
                        st.session_state["add_job"] = False
                        job_description_data = response.json()
                        # On success, automatically process the job description.
                        # However this slows down the creation of the job description as the
                        # user needs to wait for the parsing to finish (and there is no way to do that in the background)
                        # TODO: we need to think about how to handle this
                        # Maybe it should be a background task of the POST request?
                        # OR maybe we should have a button to trigger it?
                        response = requests.get(
                            f"{API_ENDPOINT}/{job_description_data['id']}/process",
                            timeout=360,
                        )
                        if response:
                            st.success("Job description processed!")
                        else:
                            st.error("Failed to process job description")
                            st.write(response)
                    else:
                        st.error("Failed to add job description")


def list_job_descriptions_and_cvs(job_descriptions: List[Dict[str, str]]) -> None:
    """List the job descriptions and CVs.

    :param job_descriptions: The job descriptions to list.
    """
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
                st.markdown(
                    f"<div style='white-space: normal;'>{job['description']}</div>",
                    unsafe_allow_html=True,
                )
                # Display parsed job description as table using the ExtractSkills model
                parsed_job_description = get_parsed_job_description(job["id"])
                if parsed_job_description:
                    # Convert the SkillsExtract to table data
                    st.subheader("Parsed Skills")
                    display_skills_by_category_and_type(parsed_job_description)
                if st.button("Edit job description", key=f"edit_{job['id']}"):
                    # Enter edit mode and open the expander
                    st.session_state[edit_key] = True
                    st.session_state[expander_key] = True

            # DISPLAY CV-RELATED CONTENT
            st.markdown("<br>", unsafe_allow_html=True)
            upload_pdf(job["id"])

            # ADD WEIGHTS SLIDERS
            display_weights_sliders(job["id"])

            # DISPLAY RECENT CVs
            # TODO: change this to highest ranked CV based on scores
            st.markdown("<br>", unsafe_allow_html=True)
            display_recent_cvs(job["id"], limit="10")

            display_delete_job_description_button(job["id"])


def toggle_add_job_form():
    """Toggle the display of the form to add a new job description."""
    st.session_state["add_job"] = not st.session_state.get("add_job", False)


def display_job_descriptions() -> None:
    """Display the job descriptions."""

    # DISPLAY FORM TO ADD NEW JOB DESCRIPTION
    # Initialize the session state key for the form display state
    if "add_job" not in st.session_state:
        st.session_state["add_job"] = False
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Add new job")
    st.button("Add new job listing", on_click=toggle_add_job_form)
    create_new_job_description_form()

    # DISPLAY SUBHEADER
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("Job Descriptions")

    # DISPLAY NESTED LIST OF JOB DESCRIPTIONS AND CVS
    job_descriptions = get_job_descriptions(limit=10)
    list_job_descriptions_and_cvs(job_descriptions)
