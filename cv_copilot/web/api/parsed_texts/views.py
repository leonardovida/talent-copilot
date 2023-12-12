from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from cv_copilot.db.dao.texts import ParsedTextDAO
from cv_copilot.db.dependencies import get_db_session
from cv_copilot.web.dto.texts.schema import ParsedTextDTO

router = APIRouter()


async def get_parsed_text_dao(
    session: AsyncSession = Depends(get_db_session),
) -> ParsedTextDAO:
    """Dependency for PDFDAO.

    :param session: AsyncSession dependency.
    :return: PDFDAO instance.
    """
    return ParsedTextDAO(session)


@router.get("/{pdf_id}/", response_model=ParsedTextDTO)
async def get_parsed_text(
    pdf_id: int,
    parsed_text_dao: ParsedTextDAO = Depends(get_parsed_text_dao),
) -> ParsedTextDTO:
    """Get the text for a given image ID.

    :param pdf_id: ID of the image to retrieve text for.
    :param text_dao: The TextDAO object to use for database operations.
    :return: TextDTO of the retrieved text.
    :raises HTTPException: If the text is not found.
    """
    parsed_text = await parsed_text_dao.get_parsed_text_by_id(pdf_id)
    if parsed_text is None:
        raise HTTPException(status_code=404, detail="Text not found")
    return ParsedTextDTO.from_orm(parsed_text)
