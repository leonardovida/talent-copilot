import base64
import logging
from io import BytesIO
from typing import List

import pdf2image


def encode_pdf_pages(pdf: bytes) -> List[str]:
    """
    Converts each page of a PDF file to JPG images and encodes them in base64.

    TODO: currently this function fetches the entire PDF
        from the database. This is not necessary, we should only need the PDF file path
        from the database and get the PDF file from storage (e.g. S3)

    :param pdf: The PDF file to convert to JPG.
    :return: encoded_images: List of base64 encoded images.
    :raises Exception: If the PDF cannot be converted to JPG.
    """
    encoded_images = []
    try:
        images = pdf2image.pdf2image.convert_from_bytes(pdf)

        for image in images:
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            encoded_images.append(img_str)

    except Exception as e:
        logging.error(f"Error in converting PDF to JPG: {e}")
        raise

    return encoded_images
