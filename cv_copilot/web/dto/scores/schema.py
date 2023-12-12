from pydantic import BaseModel

from cv_copilot.db.models.scores import ScoreModel


class ScoreModelDTO(BaseModel):
    """
    DTO for Score models.

    It returns this when accessing Score from the API.
    """

    id: int
    pdf_id: int
    job_description_id: int
    parsed_job_description_id: int
    score: float
    created_date: str

    @classmethod
    def from_orm(cls, obj: ScoreModel) -> "ScoreModelDTO":
        """Create a ScoreModelDTO from a ScoreModel.

        :param obj: The ScoreModelDTO to create a DTO from.
        :return: The created ScoreModelDTO.
        """
        return cls(
            id=obj.id,
            pdf_id=obj.pdf_id,
            job_description_id=obj.job_description_id,
            parsed_job_description_id=obj.parsed_job_description_id,
            score=obj.score,
            created_date=obj.created_date.isoformat(),
        )
