import asyncio
import logging

from cv_copilot.db.dao.images import ImageDAO
from cv_copilot.db.dao.pdfs import PDFDAO
from cv_copilot.db.dao.texts import TextDAO
from cv_copilot.db.models.texts import TextModel
from cv_copilot.services.llm.utils import get_text_from_image
from cv_copilot.services.pdf.processing import encode_pdf_pages
from cv_copilot.settings import settings


async def process_pdf_workflow(
    pdf_id: int,
    pdf_dao: PDFDAO,
    image_dao: ImageDAO,
    text_dao: TextDAO,
) -> TextModel:
    """
    Process the PDF workflow which includes converting PDF to JPG and then to text.

    :param pdf_id: The ID of the PDF to process.
    :param text_dao: The TextDAO object to use for database operations.
    :return: The text of the PDF.
    """
    try:
        await convert_pdf_to_jpg(pdf_id, pdf_dao, image_dao)
        text = await convert_jpg_to_text(pdf_id, image_dao)
        return await text_dao.save_text(pdf_id=pdf_id, text=text)
    except Exception as e:
        logging.error(f"Error processing PDF workflow for PDF ID {pdf_id}: {e}")
        raise


async def convert_pdf_to_jpg(
    pdf_id: int,
    pdf_dao: PDFDAO,
    image_dao: ImageDAO,
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
        pdf=pdf,
        pdf_id=pdf_id,
    )

    # Save the encoded images
    await image_dao.save_encoded_images(
        pdf_id=pdf_id,
        job_id=pdf.job_id,
        encoded_images=encoded_images,
    )


async def convert_jpg_to_text(pdf_id: int, image_dao: ImageDAO) -> str:
    """Convert the images of a PDF to text using OpenAI.

    #TODO: this function gets ALL images for a PDF, even if
    there are duplicates images! We should only retrieve the "latest" image

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
