from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cv_copilot.db.base import Base


class TextModel(Base):
    """Model for PDFs."""

    __tablename__ = "texts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pdf_id: Mapped[int] = mapped_column(ForeignKey("pdfs.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=True)
    created_date = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    pdf = relationship("PDFModel", back_populates="text")
    parsed_text = relationship(
        "ParsedTextModel",
        back_populates="job_description",
        uselist=False,
    )

    def __repr__(self):
        return f"<TextModel(id={self.id}, pdf_id={self.pdf_id})>"
