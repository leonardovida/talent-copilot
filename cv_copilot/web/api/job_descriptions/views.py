from typing import Dict, List

from fastapi import APIRouter, Depends

from cv_copilot.db.dao.job_descriptions import JobDescriptionDAO
from cv_copilot.db.models.job_descriptions import JobDescriptionModel
from cv_copilot.web.api.job_descriptions.schema import (
    JobDescriptionDTO,
    JobDescriptionInputDTO,
)

router = APIRouter()


@router.post("/", response_model=JobDescriptionDTO)
async def create_job_description(
    job_description_input: JobDescriptionInputDTO,
    job_description_dao: JobDescriptionDAO = Depends(),
) -> JobDescriptionDTO:
    """
    Store a new job description in the database.

    :param job_description_input: DTO for creating a job description model.
    :param job_description_dao: DAO for Job Descriptions models.
    :return: job_description_model: DTO of the created job description model.
    """
    return await job_description_dao.create_job_description(
        job_description_input,
    )


@router.delete("/{job_description_id}", response_model=dict)
async def delete_job_description(
    job_description_id: int,
    job_description_dao: JobDescriptionDAO = Depends(),
) -> Dict[str, str]:
    """
    Delete a job description from the database.

    :param job_description_id: ID of the job description to delete.
    :param job_description_dao: DAO for Job Descriptions models.
    :return: Confirmation of deletion.
    """
    await job_description_dao.delete_job_description(job_description_id)
    return {"status": "success", "message": "Job description deleted successfully."}


@router.get("/search/", response_model=List[JobDescriptionDTO])
async def search_job_descriptions(
    query: str,
    job_description_dao: JobDescriptionDAO = Depends(),
) -> List[JobDescriptionModel]:
    """
    Search for job descriptions based on a query.

    :param query: Search query to match against job descriptions.
    :param job_description_dao: DAO for Job Descriptions models.
    :return: List of job descriptions that match the query.
    """
    return await job_description_dao.search_job_descriptions(query)


@router.get("/recent/", response_model=List[JobDescriptionDTO])
async def get_recent_job_descriptions(
    limit: int = 10,
    job_description_dao: JobDescriptionDAO = Depends(),
) -> List[JobDescriptionModel]:
    """
    Retrieve the most recent job descriptions.

    :param limit: The number of recent job descriptions to return.
    :param job_description_dao: DAO for Job Descriptions models.
    :return: List of recent job descriptions.
    """
    return await job_description_dao.get_recent_job_descriptions(limit)
