import logging
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.models.scores import ScoreModel
from cv_copilot.web.dto.scores.schema import ScoreModelDTO


class ScoreDAO:
    """Class for accessing the 'scores' table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_scores_by_pdf_id_and_job_description_id(
        self,
        pdf_id: int,
        job_description_id: int,
    ) -> Optional[ScoreModel]:
        """
        Get a Score by pdf_id and job_description_id.

        :param pdf_id: ID of the pdf.
        :param job_description_id: ID of the job description.

        :return: ScoreModel if found, else None.
        """

        result = await self.session.execute(
            select(ScoreModel)
            .where(
                ScoreModel.pdf_id == pdf_id,
                ScoreModel.job_description_id == job_description_id,
            )
            .order_by(ScoreModel.id.desc()),
        )
        score = result.scalar()
        return ScoreModelDTO.from_orm(score)

    async def save_score(
        self,
        pdf_id: int,
        job_description_id: int,
        parsed_job_description_id: int,
        score: float,
    ) -> Optional[ScoreModel]:

        """
        Save a new score.

        :param pdf_id: ID of the pdf.
        :param job_description_id: ID of the job description.
        :param parsed_job_description_id: ID of the parsed job description.

        :return: ScoreModel if found, else None.
        """

        try:
            new_score = ScoreModel(
                pdf_id=pdf_id,
                job_description_id=job_description_id,
                parsed_job_description_id=parsed_job_description_id,
                score=score,
            )

            self.session.add(new_score)
            await self.session.commit()
            await self.session.refresh(new_score)
            logging.info(f"Score has created successfully!")

            return ScoreModelDTO.from_orm(new_score)

        except Exception as e:
            logging.error(f"Error uploading PDF: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e
