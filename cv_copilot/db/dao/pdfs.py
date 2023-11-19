from typing import List, Optional

import pendulum
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.dependencies import get_db_session
from cv_copilot.db.models.pdfs import PDFModel
from cv_copilot.web.api.pdf.schema import PDFModelDTO, PDFModelInputDTO


class PDFDAO:
    """Class for accessing the 'pdfs' table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_pdf(
        self,
        pdf_input: PDFModelInputDTO,
    ) -> PDFModelDTO:
        """
        Add single pdf to session.

        :param pdf_input: DTO for creating a PDF model.
        :return: DTO of the created PDF model.
        """
        # Get current time in Datetime format.
        uploaded_date = pendulum.now().to_datetime_string()
        new_pdf = PDFModel(
            name=pdf_input.name,
            job_id=pdf_input.job_id,
            uploaded_date=uploaded_date,
            file=pdf_input.file,
            s3_url=pdf_input.s3_url,
        )
        self.session.add(new_pdf)
        await self.session.commit()
        await self.session.refresh(new_pdf)

        return PDFModelDTO(
            id=new_pdf.id,
            name=new_pdf.name,
            file=new_pdf.file,
            s3_url=new_pdf.s3_url,
        )

    async def get_all_pdfs(
        self,
        job_id: int,
        limit: int,
        offset: int,
    ) -> List[PDFModel]:
        """
        Get all PDFs for a job description (job_id) with limit/offset pagination.

        :param job_id: job_id of the job description of the PDF.
        :param limit: limit of PDF.
        :param offset: offset of PDF.
        :return: stream of PDF.
        """
        raw_pdfs = await self.session.execute(
            select(PDFModel)
            .where(PDFModel.job_id == job_id)
            .limit(limit)
            .offset(offset),
        )

        return list(raw_pdfs.scalars().fetchall())

    async def filter(
        self,
        name: Optional[str] = None,
        job_id: Optional[int] = None,
    ) -> List[PDFModel]:
        """
        Get specific PDF.

        :param name: name of the PDF.
        :param job_id: job_id of the job description of the PDF.
        :return: PDF models.
        """
        query = select(PDFModel)
        if name:
            query = query.where(PDFModel.name == name)
        if job_id:
            query = query.where(PDFModel.job_id == job_id)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())
