from datetime import datetime
from typing import List, Union

from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile
from fastapi.param_functions import Depends

from cv_copilot.db.dao.pdfs import PDFDAO
from cv_copilot.services.pdf.workflow import process_pdf_workflow
from cv_copilot.services.text_processing.workflow import process_text_workflow
from cv_copilot.web.dto.pdfs.schema import PDFModelDTO, PDFModelInputDTO

router = APIRouter()


@router.get("/", response_model=List[PDFModelDTO])
async def get_pdf(
    job_id: int,
    limit: int = 10,
    offset: int = 0,
    pdf_dao: PDFDAO = Depends(),
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
    background_tasks: BackgroundTasks,
    pdf_file: UploadFile = File(...),
    name: str = Form(...),
    job_id: int = Form(...),
    created_date: Union[str, datetime] = Form(...),
    pdf_dao: PDFDAO = Depends(),
) -> PDFModelDTO:
    """
    Store a new PDF in the database.

    :param background_tasks: Background tasks.
    :param pdf_file: PDF file to upload.
    :param name: Name of the PDF.
    :param job_id: ID of the job description related to the PDF.
    :param created_date: Date the PDF was created. Can be a string or a datetime.
    :param pdf_dao: DAO for PDFs models.
    :return: PDFModelDTO of the created PDF.
    """
    pdf_input = PDFModelInputDTO(name=name, job_id=job_id, created_date=created_date)
    pdf_model = await pdf_dao.upload_pdf(pdf_input, pdf_file)

    # Trigger background tasks to process the PDF
    # We don't want the frontend to wait for the processing to finish
    background_tasks.add_task(process_pdf_workflow, pdf_model.id)
    background_tasks.add_task(process_text_workflow, pdf_model.id)

    return pdf_model  # noqa: WPS331
