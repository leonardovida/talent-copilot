from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.dao.texts import TextDAO
from cv_copilot.db.dependencies import get_db_session
from cv_copilot.web.dto.texts.schema import TextDTO

router = APIRouter()


async def get_text_dao(
    session: AsyncSession = Depends(get_db_session),
) -> TextDAO:
    """Dependency for PDFDAO.

    :param session: AsyncSession dependency.
    :return: PDFDAO instance.
    """
    return TextDAO(session)


@router.get("/{pdf_id}/text", response_model=TextDTO)
async def get_text(pdf_id: int, text_dao: TextDAO = Depends(get_text_dao)) -> TextDTO:
    """Get the text for a given image ID.

    :param pdf_id: ID of the image to retrieve text for.
    :param text_dao: The TextDAO object to use for database operations.
    :return: TextDTO of the retrieved text.
    :raises HTTPException: If the text is not found.
    """
    text = await text_dao.get_text_by_pdf_id(pdf_id)
    if text is None:
        raise HTTPException(status_code=404, detail="Text not found")
    return TextDTO(pdf_id=pdf_id, text=text)


@router.post("/{pdf_id}/text", response_model=TextDTO)
async def save_text(
    pdf_id: int,
    text: str,
    text_dao: TextDAO = Depends(get_text_dao),
) -> TextDTO:
    """Save text for a PDF.

    :param pdf_id: ID of the PDF to save text for.
    :param text: The text to save.
    :param text_dao: The TextDAO object to use for database operations.
    :return: TextDTO of the saved text.
    """
    await text_dao.save_text(pdf_id, text)
    return TextDTO(pdf_id=pdf_id, text=text)


@router.put("/{pdf_id}/text", response_model=TextDTO)
async def update_text(
    pdf_id: int,
    text: str,
    text_dao: TextDAO = Depends(get_text_dao),
) -> TextDTO:
    """Update the text for an image.

    :param pdf_id: ID of the image to update text for.
    :param text: The new text to update.
    :param text_dao: The TextDAO object to use for database operations.
    :return: TextDTO of the updated text.
    """
    await text_dao.update_text(pdf_id, text)
    return TextDTO(pdf_id=pdf_id, text=text)
