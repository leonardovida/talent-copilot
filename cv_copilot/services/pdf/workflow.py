import asyncio
import logging

from fastapi import HTTPException
from fastapi.param_functions import Depends

from cv_copilot.db.dao.images import ImageDAO
from cv_copilot.db.dao.pdfs import PDFDAO
from cv_copilot.db.dao.texts import TextDAO
from cv_copilot.services.pdf.openai_integrations import get_text_from_image
from cv_copilot.services.pdf.pdf_processing import encode_pdf_pages
from cv_copilot.settings import settings


async def process_pdf_workflow(pdf_id: int) -> bool:
    """
    Process the PDF workflow which includes converting PDF to JPG and then to text.

    :param pdf_id: The ID of the PDF to process.
    :return: True if the process is successful, False otherwise.
    :raises: HTTPException if the PDF cannot be found.
    :raises: IOError if the PDF cannot be converted to JPG.
    :raises: Exception if the JPG cannot be converted to text.
    :raises: Exception if the text cannot be saved to the database.
    """
    try:
        await convert_pdf_to_jpg(pdf_id)
        text = await convert_jpg_to_text(pdf_id)
        TextDAO.save_text(pdf_id, text)
        return True
    except HTTPException as http_err:
        logging.error(
            f"HTTP error occurred while processing PDF with id {pdf_id}: {http_err}",
        )
        return False
    except IOError as io_err:
        logging.error(
            f"I/O error occurred while processing PDF with id {pdf_id}: {io_err}",
        )
        return False
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while processing PDF with id {pdf_id}: {e}",
        )
        return False


async def convert_pdf_to_jpg(
    pdf_id: int,
    pdf_dao: PDFDAO = Depends(),
    image_dao: ImageDAO = Depends(),
) -> None:
    """Convert a PDF to a list of JPG images.

    :param pdf_id: The ID of the PDF to convert to JPG.
    :param pdf_dao: The PDFDAO object to use for database operations.
    :param image_dao: The ImageDAO object to use for database operations.
    :return: None
    """
    # Get PDF from database using ID
    pdf = await pdf_dao.get_pdf_by_id(pdf_id=pdf_id)

    # Check if the PDF was found
    if pdf is None:
        logging.error(f"PDF with id {pdf_id} not found.")
        return

    # Proceed with encoding if PDF is found
    encoded_images = encode_pdf_pages(
        pdf=pdf.file,
        pdf_id=pdf_id,
    )

    # Save the encoded images
    await image_dao.save_encoded_images(
        pdf_id=pdf_id,
        job_id=pdf.job_id,
        encoded_images=encoded_images,
    )


async def convert_jpg_to_text(pdf_id: int, image_dao: ImageDAO = Depends()) -> str:
    """Convert the images of a PDF to text using OpenAI.

    :param: pdf_id: The ID of the PDF to convert to text.
    :param: image_dao: The ImageDAO object to use for database operations.
    :return: The full text of the PDF.
    """
    # Get all the ImageModel objects for the PDF given an ID
    # and get all the images
    images = await image_dao.get_images_by_id(pdf_id)

    # Create a list of coroutines for the API calls
    tasks = [get_text_from_image(image.encoded_image) for image in images]

    # Convert each image to text using OpenAI
    # and save the text back to the database
    pdf_full_text = ""
    for num in range(0, len(tasks), settings.parallel_tasks):
        responses = await asyncio.gather(
            *tasks[num : num + settings.parallel_tasks],  # noqa: WPS221
        )
        for resp in responses:
            pdf_full_text = "".join(
                [pdf_full_text, resp.json()["choices"][0]["message"]["content"]],
            )

    return pdf_full_text


# async def extract_skills_job_description(pdf_id: int):
#     """Retrieve the job description.

#     :param pdf_id: The ID of the PDF to retrieve the job description for.
#     """


# async def extract_skills_cv(pdf_id: int):
#     """Retrieve the job description.

#     :param pdf_id: The ID of the PDF to retrieve the job description for.
#     """


# async def evaluate_cv(pdf_id: int):
#     """Evaluate the CV.

#     :param pdf_id: The ID of the PDF to evaluate.
#     """
