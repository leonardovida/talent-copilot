from fastapi import APIRouter
from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import ConnectionPool, Redis

from cv_copilot.services.scorer.score_calculation import score_calculation
from cv_copilot.db.dao.scores import ScoreDAO
from cv_copilot.db.dao.texts import ParsedTextDAO
from cv_copilot.db.dao.job_descriptions import ParsedJobDescriptionDAO

from cv_copilot.db.dependencies import get_db_session
from cv_copilot.web.dto.scores.schema import ScoreModelDTO


router = APIRouter()

def get_dao_dependency(dao_class):
    async def dependency(session: AsyncSession = Depends(get_db_session)) -> dao_class:
        return dao_class(session)

    return dependency

get_score_dao = get_dao_dependency(ScoreDAO)
get_parsed_text_dao = get_dao_dependency(ParsedTextDAO)
get_job_description_dao = get_dao_dependency(ParsedJobDescriptionDAO)

@router.post("process/{pdf_id}/{job_description_id}", response_model=ScoreModelDTO)
async def get_scores(
    pdf_id: int, 
    job_description_id: int,
    score_dao: ScoreDAO = Depends(get_score_dao),
    parsed_text_dao: ParsedTextDAO = Depends(get_parsed_text_dao),
    parsed_job_description_dao: ParsedJobDescriptionDAO = Depends(get_job_description_dao),
) -> ScoreModelDTO:
    
    """Process a new Score.

    :param pdf_id: ID of the pdf.
    :param job_description_id: ID of the job description
    :param score_dao: The ScoreDAO object to use for database operations.
    :param parsed_text_dao: The ParsedTextDAO object to use for database operations.
    :param parsed_job_description_dao: The ParsedJobDescriptionDAO object to use for database operations.
    :return: ScoreModelDTO of the retrieved score.
    :raises HTTPException: If the score is not found.
    """

    parsed_text_result = await parsed_text_dao.get_parsed_text_by_pdf_id_and_job_id(pdf_id=pdf_id, job_description_id=job_description_id)
    parsed_job_descriptions = await parsed_job_description_dao.get_parsed_job_description_by_id(job_description_id)
    result = await score_calculation(parsed_text=parsed_text_result)

    response = await score_dao.save_score(pdf_id=pdf_id, 
                        job_description_id=job_description_id,
                        parsed_job_description_id = parsed_job_descriptions.id,
                        score=result['score'],

                        )

    if response is None:
        raise HTTPException(status_code=404, detail="Score not found")
    
    return response


@router.get("/{pdf_id}/{job_description_id}", response_model=ScoreModelDTO)
async def get_last_score(
    pdf_id: int, 
    job_description_id: int,
    score_dao: ScoreDAO = Depends(get_score_dao),
) -> ScoreModelDTO:
    
    #TODO Update description
    """Get last Score.

    :param pdf_id: ID of the pdf.
    :param job_description_id: ID of the job description
    :param score_dao: The ScoreDAO object to use for database operations.
    :return: ScoreModelDTO of the retrieved score.
    :raises HTTPException: If the score is not found.
    """


    response = await score_dao.get_scores_by_pdf_id_and_job_description_id(pdf_id=pdf_id, job_description_id=job_description_id)
    
    if response is None:
        raise HTTPException(status_code=404, detail="Score not found")
    
    return response