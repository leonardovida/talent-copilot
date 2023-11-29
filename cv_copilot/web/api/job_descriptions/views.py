from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.dao.job_descriptions import JobDescriptionDAO
from cv_copilot.db.dependencies import get_db_session
from cv_copilot.services.text_processing.workflow import (
    process_job_description_workflow,
)
from cv_copilot.web.dto.job_description.schema import (
    JobDescriptionDTO,
    JobDescriptionInputDTO,
)

router = APIRouter()


async def get_job_description_dao(
    session: AsyncSession = Depends(get_db_session),
) -> JobDescriptionDAO:
    """Dependency for JobDescriptionDAO.

    :param session: AsyncSession dependency.
    :return: JobDescriptionDAO instance.
    """
    return JobDescriptionDAO(session)


@router.post("/", response_model=JobDescriptionDTO)
async def create_job_description(
    job_description_input: JobDescriptionInputDTO,
    job_description_dao: JobDescriptionDAO = Depends(get_job_description_dao),
) -> JobDescriptionDTO:
    """
    Store a new job description in the database.

    :param job_description_input: DTO for creating a job description model.
    :param job_description_dao: DAO for Job Descriptions models.
    :return: job_description_model: DTO of the created job description model.
    """
    return await job_description_dao.create_job_description(job_description_input)


@router.get("/", response_model=List[JobDescriptionDTO])
async def get_job_descriptions(
    limit: int = 10,
    offset: int = 0,
    job_description_dao: JobDescriptionDAO = Depends(get_job_description_dao),
) -> List[JobDescriptionDTO]:
    """
    Retrieve the most recent job descriptions.

    :param limit: The number of recent job descriptions to return.
    :param job_description_dao: DAO for Job Descriptions models.
    :return: List of recent job descriptions.
    :raises HTTPException: If no job descriptions are found.
    """
    list_job_descriptions = await job_description_dao.get_all_job_descriptions(
        limit,
        offset,
    )
    if list_job_descriptions is None:
        raise HTTPException(
            status_code=404,  # noqa: WPS432
            detail="No job description found",
        )
    return list_job_descriptions


@router.get("/{job_description_id}/", response_model=JobDescriptionDTO)
async def get_job_description_by_id(
    job_description_id: int,
    job_description_dao: JobDescriptionDAO = Depends(get_job_description_dao),
) -> JobDescriptionDTO:
    """
    Retrieve a job description by its ID.

    :param job_description_id: ID of the job description to retrieve.
    :param job_description_dao: DAO for Job Descriptions models.
    :return: The retrieved job description.
    :raises HTTPException: If the job description is not found.
    """
    job_description = await job_description_dao.get_job_description_by_id(
        job_description_id,
    )
    if job_description is None:
        raise HTTPException(
            status_code=404,  # noqa: WPS432
            detail="Job description not found",
        )
    return JobDescriptionDTO.from_orm(job_description)


@router.put("/{job_description_id}/", response_model=JobDescriptionDTO)
async def update_job_description(
    job_description_id: int,
    job_description_input: JobDescriptionInputDTO,
    job_description_dao: JobDescriptionDAO = Depends(get_job_description_dao),
) -> JobDescriptionDTO:
    """
    Update a job description in the database.

    :param job_description_id: ID of the job description to update.
    :param job_description_input: DTO for updating a job description model.
    :param job_description_dao: DAO for Job Descriptions models.
    :return: job_description_model: DTO of the updated job description model.
    :raises HTTPException: If the job description is not found.
    """
    updated_job_description = await job_description_dao.update_job_description(
        job_description_id,
        job_description_input,
    )
    if updated_job_description is None:
        raise HTTPException(
            status_code=404,  # noqa: WPS432
            detail="Job description not found",
        )
    return updated_job_description


@router.delete("/{job_description_id}", response_model=dict)
async def delete_job_description(
    job_description_id: int,
    job_description_dao: JobDescriptionDAO = Depends(get_job_description_dao),
) -> Dict[str, str]:
    """
    Delete a job description from the database.

    :param job_description_id: ID of the job description to delete.
    :param job_description_dao: DAO for Job Descriptions models.
    :return: Confirmation of deletion.
    """
    await job_description_dao.delete_job_description(job_description_id)
    return {"status": "success", "message": "Job description deleted successfully."}


@router.get("/{job_description_id}/process/", response_model=dict)
async def process_job_description(
    job_description_id: int,
    job_description_dao: JobDescriptionDAO = Depends(get_job_description_dao),
) -> Dict[str, str]:
    """
    Process a job description.

    :param job_description_id: ID of the job description to process.
    :param job_description_dao: DAO for Job Descriptions models.
    :return: Confirmation of processing.
    """
    job_description = await job_description_dao.get_job_description_by_id(
        job_description_id,
    )
    if job_description is None:
        raise HTTPException(
            status_code=404,  # noqa: WPS432
            detail="Job description not found",
        )
    result = await process_job_description_workflow(job_description)
    if result is False:
        raise HTTPException(
            status_code=500,  # noqa: WPS432
            detail="Job description processing failed",
        )
    return {"status": "success", "message": "Job description processed successfully."}
