import logging

from fastapi import HTTPException


async def process_text_workflow(pdf_id: int) -> bool:
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
        # await extract_skills_job_description(pdf_id)
        # await extract_skills_cv(pdf_id)
        # await evaluate_cv(pdf_id)
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
