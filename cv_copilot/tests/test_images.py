import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.dao.images import ImageDAO
from cv_copilot.db.models.images import ImageModel
from cv_copilot.web.dto.job_description.schema import JobDescriptionDTO
from cv_copilot.web.dto.pdfs.schema import PDFModelDTO


@pytest.mark.anyio
async def test_upload_image(
    dbsession: AsyncSession,
    create_job_description: JobDescriptionDTO,
    create_pdf: PDFModelDTO,
) -> None:
    """Tests image upload.

    :param dbsession: AsyncSession fixture.
    :param create_job_description: JobDescriptionDTO fixture.
    :param create_pdf: PDFModelDTO fixture.
    """
    dao = ImageDAO(dbsession)
    test_encoded_image = "data:image/jpeg;base64,/9j/4AAQSkZJR"

    # Create an ImageModel instance for testing upload
    image_instance = ImageModel(
        pdf_id=create_pdf.id,
        job_id=create_job_description.id,
        encoded_image=test_encoded_image,
        text=None,
    )

    # Upload the image using the DAO
    uploaded_image = await dao.add_image(image_instance)

    # Verify the image was stored in the database
    assert uploaded_image is not None
    assert uploaded_image.pdf_id == create_pdf.id
    assert uploaded_image.job_id == create_job_description.id
    assert uploaded_image.encoded_image == test_encoded_image

    images = await dao.get_images_by_id(create_pdf.id)
    assert len(images) > 0  # noqa: WPS507
