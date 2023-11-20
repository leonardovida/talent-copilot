import asyncio

import pytest
import pytest_mock
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.dao.images import ImageDAO
from cv_copilot.db.models.images import ImageModel
from cv_copilot.services.pdf.workflow import (
    convert_jpg_to_text,
    convert_pdf_to_jpg,
    process_pdf_workflow,
)


@pytest.mark.anyio
async def test_upload_image(
    dbsession: AsyncSession,
) -> None:
    """Tests image upload."""
    dao = ImageDAO(dbsession)
    test_pdf_id = 1  # Assuming there is a PDF with ID 1 for testing
    test_job_id = 1  # Assuming there is a job with ID 1 for testing
    test_encoded_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."

    # Create an ImageModel instance for testing upload
    image_instance = ImageModel(
        pdf_id=test_pdf_id,
        job_id=test_job_id,
        encoded_image=test_encoded_image,
        text=None,
    )

    # Upload the image using the DAO
    uploaded_image = await dao.add_image(image_instance)

    # Verify the image was stored in the database
    assert uploaded_image is not None
    assert uploaded_image.pdf_id == test_pdf_id
    assert uploaded_image.job_id == test_job_id
    assert uploaded_image.encoded_image == test_encoded_image


@pytest.mark.anyio
async def test_get_images_by_pdf_id(
    dbsession: AsyncSession,
) -> None:
    """Tests retrieval of images by PDF ID."""
    dao = ImageDAO(dbsession)
    test_pdf_id = 1  # Assuming there is a PDF with ID 1 for testing

    # Assuming we have already uploaded images for this PDF, we retrieve them
    images = await dao.get_images_by_id(test_pdf_id)

    # Verify that we received images for the correct PDF
    assert len(images) > 0  # noqa: WPS507
    for image in images:
        assert image.pdf_id == test_pdf_id


@pytest.mark.anyio
async def test_convert_pdf_to_jpg(
    dbsession: AsyncSession,
    mocker: pytest_mock.MockerFixture,
) -> None:
    """Tests the conversion of a PDF to JPG images."""
    # Mock the encode_pdf_pages function
    mocker.patch(
        "cv_copilot.services.pdf.pdf_processing.encode_pdf_pages",
        return_value=["data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."],
    )

    # Call the convert_pdf_to_jpg function
    await convert_pdf_to_jpg(pdf_id=1)  # Assuming there is a PDF with ID 1 for testing

    # Verify that images have been saved to the database
    dao = ImageDAO(dbsession)
    images = await dao.get_images_by_id(1)
    assert len(images) > 0  # noqa: WPS507


@pytest.mark.anyio
async def test_convert_jpg_to_text(
    mocker: pytest_mock.MockerFixture,
) -> None:
    """Tests the conversion of JPG images to text."""
    # Mock the get_text_from_image function
    mocker.patch(
        "cv_copilot.services.pdf.openai_integrations.get_text_from_image",
        return_value=asyncio.Future(),
    )
    mocker.patch(
        "cv_copilot.services.pdf.openai_integrations.get_text_from_image.return_value",
        side_effect=lambda image: {
            "choices": [{"message": {"content": "Extracted text"}}],
        },
    )

    # Call the convert_jpg_to_text function
    text = await convert_jpg_to_text(
        pdf_id=1,
    )  # Assuming there is a PDF with ID 1 for testing

    # Verify that the text has been extracted correctly
    assert text == "Extracted text"


@pytest.mark.anyio
async def test_process_pdf_workflow(
    mocker: pytest_mock.MockerFixture,
) -> None:
    """Tests the entire workflow of processing a PDF."""
    # Mock the necessary functions
    mocker.patch(
        "cv_copilot.services.pdf.pdf_processing.encode_pdf_pages",
        return_value=["data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."],
    )
    mocker.patch(
        "cv_copilot.services.pdf.openai_integrations.get_text_from_image",
        return_value=asyncio.Future(),
    )
    mocker.patch(
        "cv_copilot.services.pdf.openai_integrations.get_text_from_image.return_value",
        side_effect=lambda image: {
            "choices": [{"message": {"content": "Extracted text"}}],
        },
    )

    # Call the process_pdf_workflow function
    success = await process_pdf_workflow(
        pdf_id=1,
    )  # Assuming there is a PDF with ID 1 for testing

    # Verify that the workflow completed successfully
    assert success is True
