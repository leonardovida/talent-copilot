import json

from pydantic import BaseModel

from cv_copilot.db.models.texts import ParsedTextModel, TextModel


class TextDTO(BaseModel):
    """DTO for Text models."""

    pdf_id: int
    text: str

    @classmethod
    def from_orm(cls, obj: TextModel) -> "TextDTO":
        """Create a JobDescriptionDTO from a JobDescriptionModel.

        :param obj: The JobDescriptionModel to create a DTO from.
        :return: The created JobDescriptionDTO.
        """
        return cls(
            pdf_id=obj.pdf_id,
            text=str(obj.text),
        )


class ParsedTextDTO(BaseModel):
    """DTO for Parsed Text models."""

    id: int
    job_description_id: int
    parsed_skills: dict

    @classmethod
    def from_orm(cls, obj: ParsedTextModel) -> "ParsedTextDTO":
        """Create a ParsedTextDTO from a ParsedTextModel.

        :param obj: The ParsedTextModel to create a DTO from.
        :return: The created ParsedTextDTO.
        """
        parsed_skills = json.loads(obj.parsed_skills) if obj.parsed_skills else {}

        return cls(
            id=obj.id,
            job_description_id=obj.job_description_id,
            parsed_skills=obj.parsed_skills,
        )
