import base64
import logging
from io import BytesIO
from typing import List, Optional

import pdf2image


class PDFConversionError(Exception):
    """Exception raised when a PDF cannot be converted to JPG."""


def encode_pdf_pages(pdf: Optional[bytes]) -> List[str]:
    """
    Converts each page of a PDF file to JPG images and encodes them in base64.

    TODO: currently this function fetches the entire PDF
    from the database. This is not necessary, we should only need the PDF file path
    from the database and get the PDF file from storage (e.g. S3)

    :param pdf: The PDF file to convert to JPG.
    :return: encoded_images: List of base64 encoded images.
    :raises ValueError: If the PDF file is None.
    :raises PDFConversionError: If the PDF cannot be converted to JPG.
    """
    encoded_images = []
    try:
        if pdf is None:
            raise ValueError("PDF file is None")
        images = pdf2image.pdf2image.convert_from_bytes(pdf)

        for image in images:
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            encoded_images.append(img_str)

    except Exception as e:
        logging.error(f"Error in converting PDF to JPG: {e}")
        raise PDFConversionError(f"Error in converting PDF to JPG: {e}") from e

    return encoded_images
