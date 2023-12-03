from datetime import datetime
from typing import List, Union

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.param_functions import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.dao.job_descriptions import ParsedJobDescriptionDAO
from cv_copilot.db.dao.pdfs import PDFDAO
from cv_copilot.db.dao.texts import ParsedTextDAO
from cv_copilot.db.dependencies import get_db_session
from cv_copilot.services.pdf.workflow import process_pdf_workflow
from cv_copilot.services.text.workflow import workflow_evaluate_cv
from cv_copilot.web.dto.pdfs.schema import PDFModelDTO, PDFModelInputDTO
from cv_copilot.web.dto.texts.schema import ParsedTextDTO

router = APIRouter()


async def get_pdf_dao(
    session: AsyncSession = Depends(get_db_session),
) -> PDFDAO:
    """Dependency for PDFDAO.

    :param session: AsyncSession dependency.
    :return: PDFDAO instance.
    """
    return PDFDAO(session)


async def get_text_dao(
    session: AsyncSession = Depends(get_db_session),
) -> ParsedTextDAO:
    """Dependency for TextDAO.

    :param session: AsyncSession dependency.
    :return: TextDAO instance.
    """
    return ParsedTextDAO(session)


async def get_job_description_dao(
    session: AsyncSession = Depends(get_db_session),
) -> ParsedJobDescriptionDAO:
    """Dependency for job description DAO.

    :param session: AsyncSession dependency.
    :return: Job description DAO instance.
    """
    return ParsedJobDescriptionDAO(session)


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
    return PDFModelDTO.from_orm(pdf)


@router.post("/{pdf_id}/process", response_model=PDFModelDTO)
async def process_pdf(
    job_id: int,
    pdf_id: int,
    parsed_text_dao: ParsedTextDAO = Depends(get_text_dao),
    parsed_job_description_dao: ParsedJobDescriptionDAO = Depends(
        get_job_description_dao,
    ),
) -> ParsedTextDTO:
    """
    Trigger background tasks to process the PDF.

    :param job_id: ID of the job description related to the PDF.
    :param pdf_id: ID of the PDF to process.
    :param parsed_text_dao: DAO for ParsedText models.
    :param parsed_job_description_dao: DAO for ParsedJobDescription models.
    """
    # Trigger background tasks to process the PDF
    text = await process_pdf_workflow(pdf_id)
    parsed_text = await workflow_evaluate_cv(
        text=text,
        job_id=job_id,
        pdf_id=pdf_id,
        parsed_text_dao=parsed_text_dao,
        parsed_job_description_dao=parsed_job_description_dao,
    )
    return ParsedTextDTO.from_orm(parsed_text)
