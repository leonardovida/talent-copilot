from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.models.texts import ParsedTextModel, TextModel


class TextDAO:
    """Class for accessing the 'texts' table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_text_by_pdf_id(self, pdf_id: int) -> Optional[str]:
        """
        Retrieve the text for a given image ID.

        :param pdf_id: ID of the image to retrieve text for.
        :return: The text if found, else None.
        """
        result = await self.session.execute(
            select(TextModel.text).where(TextModel.id == pdf_id),
        )
        image_text = result.scalar_one_or_none()
        return image_text

    async def save_text(self, pdf_id: int, text: str) -> None:
        """
        Save text for a PDF.

        :param pdf_id: ID of the PDF to save text for.
        :param text: The text to save.
        """
        await self.session.execute(
            update(TextModel).where(TextModel.id == pdf_id).values(text=text),
        )
        await self.session.commit()

    async def update_text(self, pdf_id: int, text: str) -> None:
        """
        Update the text for an image.

        :param pdf_id: ID of the image to update text for.
        :param text: The new text to update.
        """
        await self.save_text(pdf_id, text)


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
