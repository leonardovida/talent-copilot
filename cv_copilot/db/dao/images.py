import logging
from typing import List, Optional

from fastapi import Depends
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.dependencies import get_db_session
from cv_copilot.db.models.images import ImageModel


class ImageDAO:
    """Class for accessing the 'images' table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_images_by_id(self, pdf_id: int) -> List[ImageModel]:
        """
        Retrieve all the parsed images given a pdf_id.

        :param pdf_id: ID of the PDF to retrieve images for.
        :return: List of ImageModel instances associated with the PDF.
        """
        result = await self.session.execute(
            select(ImageModel).where(ImageModel.pdf_id == pdf_id),
        )
        return list(result.scalars().all())

    async def add_image(self, image: ImageModel) -> ImageModel:
        """
        Add a single image to the database.

        :param image: ImageModel instance to add.
        :return: The added ImageModel instance.
        """
        self.session.add(image)
        await self.session.commit()
        await self.session.refresh(image)
        return image

    async def save_encoded_images(
        self,
        pdf_id: int,
        job_id: int,
        encoded_images: list[str],
    ) -> List[int]:
        """
        Save encoded images to the database, each separately.

        :param pdf_id: ID of the PDF related to the images.
        :param job_id: ID of the job description related to the images.
        :param encoded_images: List of base64 encoded images.
        :return: List of IDs of the added images.
        """
        # Create a list of ImageModel instances
        parsed_pdf_instances = [
            ImageModel(pdf_id=pdf_id, job_id=job_id, encoded_image=image, text=None)
            for image in encoded_images
        ]

        # Add all instances to the session and commit
        self.session.add_all(parsed_pdf_instances)
        await self.session.commit()

        image_ids = []
        for image in parsed_pdf_instances:
            await self.session.refresh(image)
            image_ids.append(image.id)

        logging.info(f"Saved {len(image_ids)} images to the database for PDF {pdf_id}")
        return image_ids

    async def get_image_by_id(self, image_id: int) -> Optional[ImageModel]:
        """
        Retrieve a single image by its ID.

        :param image_id: ID of the image to retrieve.
        :return: ImageModel instance if found, else None.
        """
        result = await self.session.execute(
            select(ImageModel).where(ImageModel.id == image_id),
        )
        return result.scalars().first()

    async def delete_image_by_id(self, image_id: int) -> None:
        """
        Delete a single image by its ID.

        :param image_id: ID of the image to delete.
        """
        await self.session.execute(
            delete(ImageModel).where(ImageModel.id == image_id),
        )
        await self.session.commit()

    async def update_image_text(self, image_id: int, text: str) -> None:
        """
        Update the 'text' column of an image with the parsed text.

        :param image_id: ID of the image to update.
        :param text: Parsed text to be saved in the 'text' column.
        """
        await self.session.execute(
            update(ImageModel).where(ImageModel.id == image_id).values(text=text),
        )
        await self.session.commit()
