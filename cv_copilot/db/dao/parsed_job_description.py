from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.models.job_descriptions import ParsedJobDescriptionModel


class ParsedJobDescriptionDAO:
    """Class for accessing the 'parsed_job_descriptions' table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_parsed_job_description_by_id(
        self,
        job_description_id: int,
    ) -> Optional[ParsedJobDescriptionModel]:
        """Get a single parsed job description by its ID.

        :param job_description_id: ID of the parsed job description to retrieve.
        :return: ParsedJobDescriptionModel if found, else None.
        """
        result = await self.session.execute(
            select(ParsedJobDescriptionModel).where(
                ParsedJobDescriptionModel.job_description_id == job_description_id,
            ),
        )
        return result.scalar_one_or_none()

    async def save_parsed_job_description(
        self,
        job_description_id: int,
        parsed_text: dict,
    ) -> None:
        """Save a parsed job description to the database.

        :param job_description_id: ID of the job description to save.
        :param parsed_text: Parsed text to save.
        """
        new_parsed_job_description = ParsedJobDescriptionModel(
            job_description_id=job_description_id,
            parsed_text=parsed_text,
        )
        self.session.add(new_parsed_job_description)
        await self.session.commit()

    async def update_parsed_job_description(
        self,
        job_description_id: int,
        parsed_text: dict,
    ) -> None:
        """Update a parsed job description in the database.

        :param job_description_id: ID of the job description to update.
        :param parsed_text: Parsed text to update.
        """
        await self.session.execute(
            update(ParsedJobDescriptionModel)
            .where(ParsedJobDescriptionModel.job_description_id == job_description_id)
            .values(parsed_text=parsed_text),
        )
        await self.session.commit()
