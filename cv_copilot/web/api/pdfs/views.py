from typing import List

from fastapi import APIRouter, BackgroundTasks
from fastapi.param_functions import Depends

from cv_copilot.db.dao.pdfs import PDFDAO
from cv_copilot.db.models.pdfs import PDFModel
from cv_copilot.services.pdf.manager import process_pdf_workflow, process_text_workflow
from cv_copilot.web.api.pdfs.schema import PDFModelDTO, PDFModelInputDTO

router = APIRouter()


@router.get("/", response_model=List[PDFModelDTO])
async def get_pdf(
    job_id: int,
    limit: int = 10,
    offset: int = 0,
    pdf_dao: PDFDAO = Depends(),
) -> List[PDFModel]:
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
    pdf_input: PDFModelInputDTO,
    pdf_dao: PDFDAO = Depends(),
) -> PDFModelDTO:
    """
    Store a new PDF in the database.

    :param background_tasks: Background tasks.
    :param pdf_input: DTO for creating a PDF model.
    :param pdf_dao: DAO for PDFs models.
    :return: pdf_model: DTO of the created PDF model.
    """
    pdf_model = await pdf_dao.upload_pdf(pdf_input)

    # Trigger background tasks to process the PDF
    # We don't want the frontend to wait for the processing to finish
    background_tasks.add_task(process_pdf_workflow, pdf_model.id)
    background_tasks.add_task(process_text_workflow, pdf_model.id)

    return pdf_model  # noqa: WPS331
