from pydantic import BaseModel


class TextDTO(BaseModel):
    """DTO for Text models."""

    pdf_id: int
    text: str
