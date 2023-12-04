import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.dao.job_descriptions import ParsedJobDescriptionDAO
from cv_copilot.db.dependencies import get_db_session
from cv_copilot.web.dto.job_description.schema import ParsedJobDescriptionDTO

router = APIRouter()


async def get_parsed_job_description_dao(
    session: AsyncSession = Depends(get_db_session),
) -> ParsedJobDescriptionDAO:
    """Dependency for ParsedJobDescriptionDAO.

    :param session: AsyncSession dependency.
    :return: ParsedJobDescriptionDAO instance.
    """
    return ParsedJobDescriptionDAO(session)


@router.get("/{job_id}/", response_model=ParsedJobDescriptionDTO)
async def get_parsed_job_description_by_id(
    job_id: int,
    parsed_job_description_dao: ParsedJobDescriptionDAO = Depends(
        get_parsed_job_description_dao,
    ),
) -> ParsedJobDescriptionDTO:
    """
    Retrieve the most recent job descriptions.

    :param parsed_job_description_dao: DAO for Job Descriptions models.
    :return: ParsedJobDescriptionDTO instance.
    :raises HTTPException: If no job descriptions are found.
    """
    parsed_job_descriptions = (
        await parsed_job_description_dao.get_parsed_job_description_by_id(job_id)
    )
    logging.info(f"{parsed_job_descriptions}")
    if parsed_job_descriptions is None:
        raise HTTPException(
            status_code=404,  # noqa: WPS432
            detail="No parsed job description found",
        )
    return ParsedJobDescriptionDTO.from_orm(parsed_job_descriptions)
