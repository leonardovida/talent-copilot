import logging
from typing import List, Optional

from fastapi import Depends, HTTPException, UploadFile
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.dependencies import get_db_session
from cv_copilot.db.models.pdfs import PDFModel
from cv_copilot.web.dto.pdfs.schema import PDFModelDTO, PDFModelInputDTO


class PDFDAO:
    """Class for accessing the 'pdfs' table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def upload_pdf(
        self,
        pdf_input: PDFModelInputDTO,
        pdf_file: UploadFile,
    ) -> PDFModelDTO:
        """
        Add single pdf to session.

        :param pdf_input: DTO for creating a PDF model.
        :param pdf_file: PDF file to upload.
        :return: DTO of the created PDF model.
        :raises HTTPException: If the PDF cannot be uploaded.
        """
        try:
            file_contents = await pdf_file.read()
            new_pdf = PDFModel(
                name=pdf_input.name,
                job_id=pdf_input.job_id,
                file=file_contents,
                s3_url=pdf_input.s3_url,
                created_date=pdf_input.created_date,
            )
            self.session.add(new_pdf)
            await self.session.commit()
            await self.session.refresh(new_pdf)
            logging.info(f"PDF file weight: {len(file_contents)}")
            return PDFModelDTO.from_orm(new_pdf)
        except Exception as e:
            logging.error(f"Error uploading PDF: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e
        finally:
            await pdf_file.close()

    async def get_pdf_by_id(
        self,
        pdf_id: int,
    ) -> Optional[PDFModel]:
        """
        Get a single PDF by its ID.

        :param pdf_id: ID of the PDF to retrieve.
        :return: PDFModel if found, else None.
        """
        result = await self.session.execute(
            select(PDFModel).where(PDFModel.id == pdf_id),
        )
        pdf = result.scalars().first()
        logging.info(f"PDF result: {pdf} - ID: {pdf_id}")
        return pdf

    async def get_all_pdfs(
        self,
        job_id: int,
        limit: int,
        offset: int,
    ) -> List[PDFModelDTO]:
        """
        Get all PDFs for a job description (job_id) with limit/offset pagination.

        The PDFs are ordered in order by recency.

        :param job_id: job_id of the job description of the PDF.
        :param limit: limit of PDF.
        :param offset: offset of PDF.
        :return: stream of PDF.
        """
        raw_pdfs = await self.session.execute(
            select(PDFModel)
            .where(PDFModel.job_id == job_id)
            .order_by(desc(PDFModel.created_date))
            .limit(limit)
            .offset(offset),
        )
        return [PDFModelDTO.from_orm(pdf) for pdf in raw_pdfs.scalars().fetchall()]

    async def filter(
        self,
        name: Optional[str] = None,
        job_id: Optional[int] = None,
    ) -> List[PDFModelDTO]:
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
        return [PDFModelDTO.from_orm(pdf) for pdf in rows.scalars().fetchall()]

    async def delete_pdf_by_id(self, pdf_id: int) -> bool:
        """
        Delete a PDF by its ID.

        :param pdf_id: ID of the PDF to delete.
        :return: True if deletion was successful, False otherwise.
        """
        try:
            pdf_to_delete = await self.get_pdf_by_id(pdf_id)
            if pdf_to_delete:
                await self.session.delete(pdf_to_delete)
                await self.session.commit()
                return True
            return False
        except Exception as e:
            logging.error(f"Error deleting PDF ID {pdf_id}: {e}")
            await self.session.rollback()
            return False
