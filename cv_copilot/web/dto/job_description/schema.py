import json
from typing import Optional

from pydantic import BaseModel, Field

from cv_copilot.db.models.job_descriptions import (
    JobDescriptionModel,
    ParsedJobDescriptionModel,
)


class JobDescriptionDTO(BaseModel):
    """
    DTO for Job Description models.

    This DTO is used when accessing Job Descriptions from the API.

    Attributes:
        id (int): The unique identifier for the job description.
        title (str): The title of the job description.
        description (str): The detailed description of the job.
        created_date (str): The creation date in ISO 8601 format.
        updated_date (str): The update date in ISO 8601 format, if available.

    Note:
        The 'created_date' and 'updated_date' fields are strings formatted in ISO 8601.
        In the future, we could consider using actual datetime objects for these fields
        and validate them with Pydantic's validators, as shown in the commented example below.

        # @validator('created_date', 'updated_date', pre=True, always=True)
        # def default_datetime(cls, value):
        #     return value or datetime.now().isoformat()
    """

    id: int
    title: str
    description: str
    created_date: str
    updated_date: Optional[str] = None

    @classmethod
    def from_orm(cls, obj: JobDescriptionModel) -> "JobDescriptionDTO":
        """Create a JobDescriptionDTO from a JobDescriptionModel.

        :param obj: The JobDescriptionModel to create a DTO from.
        :return: The created JobDescriptionDTO.
        """
        return cls(
            id=obj.id,
            title=str(obj.title),
            description=str(obj.description) if obj.description is not None else "",
            created_date=obj.created_date.isoformat(),
            updated_date=obj.updated_date.isoformat() if obj.updated_date else None,
        )


class JobDescriptionInputDTO(BaseModel):
    """DTO for creating a Job Description model.

    This represents the model of the job description to our service.
    """

    title: str = Field(..., description="The title of the job description")
    description: str = Field(..., description="The detailed description of the job")


class ParsedJobDescriptionDTO(BaseModel):
    """
    DTO for Parsed Job Description models.

    This DTO is used when accessing Parsed Job Descriptions from the API.
    """

    id: int
    job_description_id: int
    parsed_skills: dict
    created_date: str

    @classmethod
    def from_orm(cls, obj: ParsedJobDescriptionModel) -> "ParsedJobDescriptionDTO":
        """Create a ParsedJobDescriptionDTO from a JobDescriptionModel.

        :param obj: The JobDescriptionModel to create a DTO from.
        :return: The created ParsedJobDescriptionDTO.
        """
        parsed_skills = json.loads(obj.parsed_skills) if obj.parsed_skills else {}
        # parsed_skills = cast(Dict, obj.parsed_skills) if obj.parsed_skills else {}

        return cls(
            id=obj.id,
            job_description_id=obj.job_description_id,
            parsed_skills=parsed_skills,
            created_date=obj.created_date.isoformat(),
        )
