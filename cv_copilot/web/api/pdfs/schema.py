from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class PDFModelDTO(BaseModel):
    """
    DTO for PDF models.

    It returns this when accessing PDF from the API.
    """

    id: int
    name: str
    file: Optional[bytes] = None
    s3_url: Optional[HttpUrl] = None


class PDFModelInputDTO(BaseModel):
    """DTO for creating a PDF model.

    This represents the model of the uploaded PDF to our service.
    """

    name: str = Field(..., description="The name of the PDF model")
    job_id: int = Field(
        ...,
        description="The ID of the job that this PDF is associated with",
    )
    uploaded_date: str = Field(..., description="The date that this PDF was uploaded")
    file: bytes = Field(default=None, description="The actual PDF file data")
    s3_url: Optional[HttpUrl] = Field(
        default=None,
        description="The S3 URL of the PDF file",
    )
