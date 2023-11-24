from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field, HttpUrl, validator

from cv_copilot.db.models.pdfs import PDFModel


class PDFModelDTO(BaseModel):
    """
    DTO for PDF models.

    It returns this when accessing PDF from the API.
    """

    id: int
    name: str
    job_id: int
    file: Optional[bytes] = None
    s3_url: Optional[HttpUrl] = None
    created_date: str

    @classmethod
    def from_orm(cls, obj: PDFModel) -> "PDFModelDTO":
        """Create a PDFModelDTO from a PDFModel.

        :param obj: The PDFModel to create a DTO from.
        :return: The created PDFModelDTO.
        """
        return cls(
            id=obj.id,
            job_id=obj.job_id,
            name=obj.name,
            file=obj.file,
            s3_url=obj.s3_url,
            created_date=obj.created_date.isoformat(),
        )


class PDFModelInputDTO(BaseModel):
    """DTO for creating a PDF model.

    This represents the model of the uploaded PDF to our service.
    """

    name: str = Field(..., description="The name of the PDF model")
    job_id: int = Field(
        ...,
        description="The ID of the job that this PDF is associated with",
    )
    created_date: Union[datetime, str] = Field(
        ...,
        description="The date that this PDF was uploaded",
    )
    s3_url: Optional[HttpUrl] = Field(
        default=None,
        description="The S3 URL of the PDF file",
    )

    @validator("created_date", pre=True)
    def parse_created_date(cls, value: Union[str, datetime]) -> datetime:  # noqa: N805
        """Parse the created_date into a datetime object.

        :param value: The value to parse.
        :return: The parsed datetime object.
        :raises ValueError: If the value is not a valid datetime.
        """
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        elif isinstance(value, datetime):
            return value
        raise ValueError(f"Invalid input for created_date: {value}")
