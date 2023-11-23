import uuid
from datetime import datetime
from io import BytesIO

import pytest
from fastapi import FastAPI, UploadFile
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.datastructures import Headers

from cv_copilot.db.dao.pdfs import PDFDAO
from cv_copilot.web.dto.job_description.schema import JobDescriptionDTO


@pytest.mark.anyio
async def test_upload_pdf(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    create_job_description: JobDescriptionDTO,
) -> None:
    """Tests PDF upload."""
    url = fastapi_app.url_path_for("upload_pdf")
    test_name = uuid.uuid4().hex
    test_job_id = (
        create_job_description.id
    )  # Use the ID from the created job description
    test_created_date = datetime(2023, 1, 1).isoformat()

    # Create a PDF file in memory
    pdf_file_content = b"%PDF-1.4..."
    pdf_file = BytesIO(pdf_file_content)
    pdf_file.name = "test.pdf"
    upload_file = UploadFile(
        filename=pdf_file.name,
        file=pdf_file,
        headers=Headers({"content-type": "application/pdf"}),
    )

    # Create form data including the file and other fields
    data = {
        "name": test_name,
        "job_id": test_job_id,
        "created_date": test_created_date,
    }

    # Send the request with both files and data
    response = await client.post(
        url,
        files={
            "pdf_file": (
                upload_file.filename,
                upload_file.file,
                upload_file.content_type,
            ),
        },
        data=data,
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
