from datetime import datetime
from typing import List, Union

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.param_functions import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.dao.pdfs import PDFDAO
from cv_copilot.db.dependencies import get_db_session
from cv_copilot.services.pdf.workflow import process_pdf_workflow
from cv_copilot.services.text_processing.workflow import evaluate_cv_workflow
from cv_copilot.web.dto.pdfs.schema import PDFModelDTO, PDFModelInputDTO

router = APIRouter()


async def get_pdf_dao(
    session: AsyncSession = Depends(get_db_session),
) -> PDFDAO:
    """Dependency for PDFDAO.

    :param session: AsyncSession dependency.
    :return: PDFDAO instance.
    """
    return PDFDAO(session)


@router.get("/", response_model=List[PDFModelDTO])
async def get_pdfs(
    job_id: int,
    limit: int = 10,
    offset: int = 0,
    pdf_dao: PDFDAO = Depends(get_pdf_dao),
) -> List[PDFModelDTO]:
    """
    Retrieve all pdfs from the database.

    :param job_id: the job_id for the jobs description related to the pdfs
    :param limit: limit of PDFs objects, defaults to 10.
    :param offset: offset of PDFs objects, defaults to 0.
    :param pdf_dao: DAO for PDFs models.
    :return: list of PDFs objects from database.
    """
    return await pdf_dao.get_all_pdfs(job_id=job_id, limit=limit, offset=offset)


@router.post("/", response_model=PDFModelDTO)
async def upload_pdf(
    pdf_file: UploadFile = File(...),
    name: str = Form(...),
    job_id: int = Form(...),
    created_date: Union[str, datetime] = Form(...),
    pdf_dao: PDFDAO = Depends(get_pdf_dao),
) -> PDFModelDTO:
    """
    Store a new PDF in the database.

    :param pdf_file: PDF file to upload.
    :param name: Name of the PDF.
    :param job_id: ID of the job description related to the PDF.
    :param created_date: Date the PDF was created. Can be a string or a datetime.
    :param pdf_dao: DAO for PDFs models.
    :return: PDFModelDTO of the created PDF.
    """
    pdf_input = PDFModelInputDTO(name=name, job_id=job_id, created_date=created_date)
    pdf_model = await pdf_dao.upload_pdf(pdf_input, pdf_file)

    return pdf_model  # noqa: WPS331


@router.get("/{pdf_id}", response_model=PDFModelDTO)
async def get_pdf(
    pdf_id: int,
    pdf_dao: PDFDAO = Depends(get_pdf_dao),
) -> PDFModelDTO:
    """
    Retrieve a single pdf from the database by its ID.

    :param pdf_id: the ID of the pdf to retrieve.
    :param pdf_dao: DAO for PDFs models.
    :return: PDFModelDTO object from the database.
    :raises HTTPException: if the pdf is not found.
    """
    pdf = await pdf_dao.get_pdf_by_id(pdf_id=pdf_id)
    if pdf is None:
        raise HTTPException(status_code=404, detail="PDF not found")
    pdf = PDFModelDTO.from_orm(pdf)
    return pdf


@router.post("/{pdf_id}/process", response_model=PDFModelDTO)
async def process_pdf(
    background_tasks: BackgroundTasks,
    pdf_id: int,
) -> None:
    """
    Trigger background tasks to process the PDF.

    :param background_tasks: Background tasks.
    :param pdf_id: ID of the PDF to process.
    """
    # Trigger background tasks to process the PDF
    background_tasks.add_task(process_pdf_workflow, pdf_id)
    background_tasks.add_task(evaluate_cv_workflow, pdf_id)
