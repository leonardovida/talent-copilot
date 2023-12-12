import logging
from typing import List

from cv_copilot.db.dao.images import ImageDAO
from cv_copilot.db.dao.pdfs import PDFDAO
from cv_copilot.db.dao.texts import TextDAO
from cv_copilot.db.models.texts import TextModel
from cv_copilot.services.llm.utils import get_text_from_image
from cv_copilot.services.pdf.processing import encode_pdf_pages


async def process_pdf_workflow(
    pdf_id: int,
    pdf_dao: PDFDAO,
    image_dao: ImageDAO,
    text_dao: TextDAO,
) -> TextModel:
    """
    Process the PDF workflow which includes converting PDF to JPG and then to text.

    TODO: verify whether the pdf was already processed and return the text if it was.

    :param pdf_id: The ID of the PDF to process.
    :param text_dao: The TextDAO object to use for database operations.
    :return: The text of the PDF.
    """
    try:
        image_ids = await convert_pdf_to_jpg(pdf_id, pdf_dao, image_dao)
        text = await convert_jpg_to_text(pdf_id, image_dao, image_ids)
        return await text_dao.save_text(pdf_id=pdf_id, text=text)
    except Exception as e:
        logging.error(f"Error processing PDF workflow for PDF ID {pdf_id}: {e}")
        raise


async def convert_pdf_to_jpg(
    pdf_id: int,
    pdf_dao: PDFDAO,
    image_dao: ImageDAO,
) -> List[int]:
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
        return []

    # Proceed with encoding if PDF is found
    encoded_images = encode_pdf_pages(
        pdf=pdf,
        pdf_id=pdf_id,
    )
    logging.info(f"Encoded {len(encoded_images)} images for PDF ID {pdf_id}")

    # Save the encoded images
    return await image_dao.save_encoded_images(
        pdf_id=pdf_id,
        job_id=pdf.job_id,
        encoded_images=encoded_images,
    )


async def convert_jpg_to_text(
    pdf_id: int,
    image_dao: ImageDAO,
    image_ids: List[int],
) -> str:
    """Convert a list of JPG images to text, one image at a time.

    :param pdf_id: The ID of the PDF to convert to text.
    :param image_dao: The ImageDAO object to use for database operations.
    :param image_ids: The IDs of the images to convert to text.
    :return: The text of the PDF.
    """
    images = await image_dao.get_images_by_ids(image_ids)
    logging.info(
        f"Starting text conversion for {len(images)} images for PDF ID {pdf_id}.",
    )

    pdf_full_text = ""
    for image in images:
        try:
            response = await get_text_from_image(image.encoded_image)
            logging.info({response.choices[0].message.content})
            pdf_full_text += response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error during processing image ID {image.id}: {e}")

    image_ids_str = ", ".join(str(image.id) for image in images)
    logging.info(f"Converted images to text for image IDs: {image_ids_str}")
    return pdf_full_text
