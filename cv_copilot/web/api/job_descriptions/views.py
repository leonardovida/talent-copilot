import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from cv_copilot.db.dao.job_descriptions import JobDescriptionDAO
from cv_copilot.web.dto.job_description.schema import (
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
    :raises HTTPException: If an error occurs while creating the job description.
    """
    try:
        return await job_description_dao.create_job_description(job_description_input)
    except SQLAlchemyError as e:
        logging.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the job description.",
        ) from e


@router.get("/{job_description_id}/", response_model=List[JobDescriptionDTO])
async def get_job_description_by_id(
    job_description_id: int,
    job_description_dao: JobDescriptionDAO = Depends(),
) -> JobDescriptionDTO:
    """
    Retrieve a job description by its ID.

    :param job_description_id: ID of the job description to retrieve.
    :param job_description_dao: DAO for Job Descriptions models.
    :return: The retrieved job description.
    :raises HTTPException: If the job description cannot be found.
    """
    job_description = await job_description_dao.get_job_description_by_id(
        job_description_id,
    )
    if job_description is None:
        raise HTTPException(
            status_code=404,  # noqa: WPS432
            detail="Job description not found",
        )
    return job_description


@router.get("/recent/", response_model=List[JobDescriptionDTO])
async def get_recent_job_descriptions(
    limit: int = 10,
    job_description_dao: JobDescriptionDAO = Depends(),
) -> List[JobDescriptionDTO]:
    """
    Retrieve the most recent job descriptions.

    :param limit: The number of recent job descriptions to return.
    :param job_description_dao: DAO for Job Descriptions models.
    :return: List of recent job descriptions.
    :raises HTTPException: If no recent job descriptions are found.
    """
    job_descriptions = await job_description_dao.get_recent_job_descriptions(limit)
    if job_descriptions is None:
        raise HTTPException(
            status_code=404,  # noqa: WPS432
            detail="No recent job descriptions found",
        )
    return job_descriptions


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
    :raises HTTPException: If the job description cannot be found.
    """
    result = await job_description_dao.delete_job_description(job_description_id)
    if result is None:
        raise HTTPException(
            status_code=404,  # noqa: WPS432
            detail="Job description not found",
        )
    return {"status": "success", "message": "Job description deleted successfully."}
