import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from cv_copilot.db.dao.pdfs import PDFDAO
from cv_copilot.web.api.pdfs.schema import PDFModelInputDTO


@pytest.mark.anyio
async def test_upload_pdf(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests PDF upload."""
    url = fastapi_app.url_path_for("upload_pdf")
    test_name = uuid.uuid4().hex
    test_job_id = 1  # Assuming there is a job with ID 1 for testing
    test_file = b"%PDF-1.4..."  # A snippet of a PDF file in bytes

    pdf_input = PDFModelInputDTO(
        name=test_name,
        job_id=test_job_id,
        created_date="2023-01-01T00:00:00",  # Example date
        file=test_file,
    )

    response = await client.post(
        url,
        json=pdf_input.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    pdf_data = response.json()
    assert pdf_data["name"] == test_name
    assert pdf_data["job_id"] == test_job_id

    # Verify the PDF was stored in the database
    dao = PDFDAO(dbsession)
    pdf_instance = await dao.get_pdf_by_id(pdf_data["id"])
    assert pdf_instance is not None
    assert pdf_instance.name == test_name


@pytest.mark.anyio
async def test_get_pdf(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests PDF retrieval."""
    dao = PDFDAO(dbsession)
    test_name = uuid.uuid4().hex
    test_job_id = 1  # Assuming there is a job with ID 1 for testing
    test_file = b"%PDF-1.4..."  # A snippet of a PDF file in bytes

    # Create a PDF instance for testing retrieval
    await dao.upload_pdf(
        PDFModelInputDTO(
            name=test_name,
            job_id=test_job_id,
            created_date="2023-01-01T00:00:00",
            file=test_file,
        ),
    )

    url = fastapi_app.url_path_for("get_pdf", job_id=test_job_id)
    response = await client.get(url)

    assert response.status_code == status.HTTP_200_OK
    pdfs = response.json()

    assert len(pdfs) > 0  # noqa: WPS507
    assert any(pdf["name"] == test_name for pdf in pdfs)


@pytest.mark.anyio
async def test_get_all_pdfs(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests retrieval of all PDFs for a specific job_id with pagination."""
    dao = PDFDAO(dbsession)
    test_job_id = 1  # Assuming there is a job with ID 1 for testing

    # Create multiple PDF instances for testing retrieval
    for _ in range(3):
        await dao.upload_pdf(
            PDFModelInputDTO(
                name=uuid.uuid4().hex,
                job_id=test_job_id,
                created_date="2023-01-01T00:00:00",
                file=b"%PDF-1.4...",  # A snippet of a PDF file in bytes
            ),
        )

    url = fastapi_app.url_path_for("get_pdf", job_id=test_job_id)
    response = await client.get(f"{url}?limit=2&offset=0")

    assert response.status_code == status.HTTP_200_OK
    pdfs = response.json()

    # Check that we received the correct number of PDFs (based on limit)
    assert len(pdfs) == 2

    # Optionally, check that the PDFs belong to the correct job_id
    for pdf in pdfs:
        assert pdf["job_id"] == test_job_id
