import logging
from typing import List, Optional

import pendulum
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.models.job_descriptions import JobDescriptionModel
from cv_copilot.web.dto.job_description.schema import (
    JobDescriptionDTO,
    JobDescriptionInputDTO,
)


class JobDescriptionDAO:
    """Class for accessing the 'job_descriptions' table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job_description(
        self,
        job_description_dto: JobDescriptionInputDTO,
    ) -> JobDescriptionDTO:
        """
        Add a single job description to the database.

        :param job_description_dto: JobDescriptionInputDTO instance to add.
        :return: The added JobDescriptionDTO instance.
        """
        created_date = pendulum.now("UTC").naive()
        new_job_description = JobDescriptionModel(
            title=job_description_dto.title,
            description=job_description_dto.description,
            created_date=created_date,
        )
        self.session.add(new_job_description)
        await self.session.commit()
        await self.session.refresh(new_job_description)
        logging.info(f"Job description created with ID: {new_job_description.id}")

        return JobDescriptionDTO.from_orm(new_job_description)

    async def get_job_description_by_id(
        self,
        job_description_id: int,
    ) -> Optional[JobDescriptionDTO]:
        """
        Get a single job description by its ID.

        :param job_description_id: ID of the job description to retrieve.
        :return: JobDescriptionDTO if found, else None.
        """
        result = await self.session.execute(
            select(JobDescriptionModel).where(
                JobDescriptionModel.id == job_description_id,
            ),
        )
        job_description = result.scalars().first()
        if job_description:
            logging.info(f"Retrieved job description with ID: {job_description_id}")
        else:
            logging.warning(f"Job description with ID {job_description_id} not found")
        return JobDescriptionDTO.from_orm(job_description) if job_description else None

    async def get_all_job_descriptions(
        self,
        limit: int,
        offset: int,
    ) -> List[JobDescriptionDTO]:
        """
        Get all job descriptions with limit/offset pagination.

        :param limit: The maximum number of job descriptions to return.
        :param offset: The offset from where to start the query.
        :return: A list of JobDescriptionDTO instances.
        """
        raw_job_descriptions = await self.session.execute(
            select(JobDescriptionModel).limit(limit).offset(offset),
        )
        job_descriptions = raw_job_descriptions.scalars().fetchall()
        logging.info(
            f"Retrieved {len(job_descriptions)} job descriptions",
        )
        return [
            JobDescriptionDTO.from_orm(job_description)
            for job_description in job_descriptions
        ]

    async def get_recent_job_descriptions(
        self,
        limit: int,
    ) -> List[JobDescriptionDTO]:
        """
        Retrieve the most recent job descriptions.

        :param limit: The number of recent job descriptions to return.
        :return: List of recent JobDescriptionDTO instances.
        """
        result = await self.session.execute(
            select(JobDescriptionModel)
            .order_by(desc(JobDescriptionModel.created_date))
            .limit(limit),
        )
        recent_job_descriptions = result.scalars().all()
        logging.info(
            f"Retrieved {len(recent_job_descriptions)} most recent job descriptions",
        )
        return [
            JobDescriptionDTO.from_orm(job_description)
            for job_description in recent_job_descriptions
        ]

    async def delete_job_description(self, job_description_id: int) -> bool:
        """
        Delete a job description by its ID.

        :param job_description_id: ID of the job description to delete.
        :return: True if the job description was deleted, False otherwise.
        """
        query = delete(JobDescriptionModel).where(
            JobDescriptionModel.id == job_description_id,
        )
        result = await self.session.execute(query)
        await self.session.commit()
        if result.rowcount == 0:
            # No rows were deleted, which means the job description was not found
            logging.warning(
                f"Delete job description with ID {job_description_id}, not found",
            )
            return False
        logging.info(f"Deleted job description with ID {job_description_id}")
        return True
