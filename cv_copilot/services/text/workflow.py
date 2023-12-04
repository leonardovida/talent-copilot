import logging

from cv_copilot.db.dao.job_descriptions import ParsedJobDescriptionDAO
from cv_copilot.db.dao.texts import ParsedTextDAO
from cv_copilot.db.models.job_descriptions import ParsedJobDescriptionModel
from cv_copilot.db.models.texts import ParsedTextModel, TextModel
from cv_copilot.services.text.extract import evaluate_cv, parse_skills_job_description
from cv_copilot.web.dto.job_description.schema import JobDescriptionModel


async def workflow_process_job_description(
    job_description: JobDescriptionModel,
    parsed_job_description_dao: ParsedJobDescriptionDAO,
) -> ParsedJobDescriptionModel:
    """Process the text in the job description

    :param job_description: The job description to process.
    :param parsed_job_description_dao: DAO for ParsedJobDescription models.
    :return: The parsed job description.
    """
    logging.info(f"Processing job description with id {job_description.id}")
    job_extract = await parse_skills_job_description(job_description)
    logging.info(f"Parsed skills: {job_extract.model_dump()}")
    parsed_job_description = (
        await parsed_job_description_dao.save_parsed_job_description(
            job_description_id=job_description.id,
            job_extract=job_extract,
        )
    )
    logging.info(f"Saved parsed job description with id {parsed_job_description.id}")
    return parsed_job_description


async def workflow_evaluate_cv(
    text: TextModel,
    job_id: int,
    pdf_id: int,
    parsed_text_dao: ParsedTextDAO,
    parsed_job_description_dao: ParsedJobDescriptionDAO,
) -> ParsedTextModel:
    """
    Process the text workflow.

    Extract skills from job description and CV and then evaluate CV.

    :param text: The text to process.
    :param parsed_text: DAO for ParsedText models.
    :return: The parsed text.
    """
    try:
        # Get the parsed job description skills from DB
        parsed_job_description = (
            await parsed_job_description_dao.get_parsed_job_description_by_id(text.id)
        )
        if parsed_job_description is None:
            raise ValueError("Parsed job description not found")
        # Get the parsed job description skills from DB
        text_extracted = await evaluate_cv(
            parsed_job_description=parsed_job_description,
            parsed_text=text,
        )
        # Save and return the parsed text
        return await parsed_text_dao.save_parsed_text(
            job_id=job_id,
            pdf_id=pdf_id,
            parsed_text=text_extracted,
        )
    except Exception as e:
        logging.error(
            f"Error evaluating CV for PDF ID {pdf_id} and Job ID {job_id}: {e}",
        )
        raise
