from typing import List, Optional

import pendulum
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.models.job_descriptions import JobDescriptionModel
from cv_copilot.web.api.job_descriptions.schema import (
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
        created_date = pendulum.now()
        new_job_description = JobDescriptionModel(
            title=job_description_dto.title,
            description=job_description_dto.description,
            created_date=created_date,
        )
        self.session.add(new_job_description)
        await self.session.commit()
        await self.session.refresh(new_job_description)

        return JobDescriptionDTO.from_orm(new_job_description)

    async def get_job_description_by_id(
        self,
        job_description_id: int,
    ) -> Optional[JobDescriptionModel]:
        """
        Get a single job description by its ID.

        :param job_description_id: ID of the job description to retrieve.
        :return: JobDescriptionModel if found, else None.
        """
        result = await self.session.execute(
            select(JobDescriptionModel).where(
                JobDescriptionModel.id == job_description_id,
            ),
        )
        return result.scalars().first()

    async def get_all_job_descriptions(
        self,
        limit: int,
        offset: int,
    ) -> List[JobDescriptionModel]:
        """
        Get all job descriptions with limit/offset pagination.

        :param limit: The maximum number of job descriptions to return.
        :param offset: The offset from where to start the query.
        :return: A list of JobDescriptionModel instances.
        """
        raw_job_descriptions = await self.session.execute(
            select(JobDescriptionModel).limit(limit).offset(offset),
        )
        return list(raw_job_descriptions.scalars().fetchall())

    async def delete_job_description(self, job_description_id: int) -> None:
        """
        Delete a job description from the database.

        :param job_description_id: ID of the job description to delete.
        """
        await self.session.execute(
            delete(JobDescriptionModel).where(
                JobDescriptionModel.id == job_description_id,
            ),
        )
        await self.session.commit()

    async def search_job_descriptions(self, query: str) -> List[JobDescriptionModel]:
        """
        Search for job descriptions based on a query.

        :param query: Search query to match against job descriptions.
        :return: List of job descriptions that match the query.
        """
        search_query = f"%{query}%"
        result = await self.session.execute(
            select(JobDescriptionModel).where(
                JobDescriptionModel.title.like(search_query)
                | JobDescriptionModel.description.like(search_query),
            ),
        )
        return list(result.scalars().all())

    async def get_recent_job_descriptions(
        self,
        limit: int,
    ) -> List[JobDescriptionModel]:
        """
        Retrieve the most recent job descriptions.

        :param limit: The number of recent job descriptions to return.
        :return: List of recent job descriptions.
        """
        result = await self.session.execute(
            select(JobDescriptionModel)
            .order_by(desc(JobDescriptionModel.created_date))
            .limit(limit),
        )
        return list(result.scalars().all())
