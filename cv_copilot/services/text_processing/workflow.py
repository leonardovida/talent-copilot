import logging

from fastapi import HTTPException

from cv_copilot.services.text_processing.cv_evaluation import evaluate_cv
from cv_copilot.services.text_processing.skills_extraction import (
    parse_skills_cv,
    parse_skills_job_description,
)
from cv_copilot.web.dto.job_description.schema import JobDescriptionModel


async def process_job_description_workflow(
    job_description: JobDescriptionModel,
) -> bool:
    """Process the text in the job description

    :param job_description: The job description to process.
    :return: True if the process is successful, False otherwise.
    """
    response = await parse_skills_job_description(job_description)
    return False


async def evaluate_cv_workflow(pdf_id: int) -> bool:
    """
    Process the text workflow.

    Extract skills from job description and CV and then evaluate CV.

    :param pdf_id: The ID of the PDF to process.
    :return: True if the process is successful, False otherwise.
    :raises: HTTPException if the PDF cannot be found.
    :raises: IOError if the PDF cannot be converted to JPG.
    :raises: Exception if the JPG cannot be converted to text.
    :raises: Exception if the text cannot be saved to the database.
    """
    try:
        await parse_skills_cv(pdf_id)
        await evaluate_cv(pdf_id)
        return True
    except HTTPException as http_err:
        logging.error(
            f"HTTP error occurred while processing text for PDF with id {pdf_id}: {http_err}",
        )
        return False
    except IOError as io_err:
        logging.error(
            f"I/O error occurred while processing text for PDF with id {pdf_id}: {io_err}",
        )
        return False
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while processing text for PDF with id {pdf_id}: {e}",
        )
        return False
