from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.models.texts import ParsedTextModel


class ParsedTextDAO:
    """Class for accessing the 'parsed_texts' table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_parsed_text_by_id(
        self,
        job_description_id: int,
    ) -> Optional[ParsedTextModel]:
        """Get a single parsed text by its ID.

        :param job_description_id: ID of the parsed text to retrieve.
        :return: ParsedTextModel if found, else None.
        """
        result = await self.session.execute(
            select(ParsedTextModel).where(
                ParsedTextModel.job_description_id == job_description_id,
            ),
        )
        return result.scalar_one_or_none()

    async def save_parsed_text(self, job_description_id: int, parsed_text: str) -> None:
        """Save a parsed text to the database.

        :param job_description_id: ID of the job description to save.
        :param parsed_text: Parsed text to save.
        """
        new_parsed_text = ParsedTextModel(
            job_description_id=job_description_id,
            parsed_text=parsed_text,
        )
        self.session.add(new_parsed_text)
        await self.session.commit()

    async def update_parsed_text(
        self,
        job_description_id: int,
        parsed_text: str,
    ) -> None:
        """Update a parsed text in the database.

        :param job_description_id: ID of the job description to update.
        :param parsed_text: Parsed text to update.
        """
        await self.session.execute(
            update(ParsedTextModel)
            .where(ParsedTextModel.job_description_id == job_description_id)
            .values(parsed_text=parsed_text),
        )
        await self.session.commit()
