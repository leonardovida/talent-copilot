from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cv_copilot.db.base import Base


class TextModel(Base):
    """Model for PDFs."""

    __tablename__ = "texts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pdf_id: Mapped[int] = mapped_column(ForeignKey("pdfs.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=True)

    pdf = relationship("PDFModel", back_populates="text")
    parsed_text = relationship(
        "ParsedTextModel",
        back_populates="job_description",
        uselist=False,
    )

    def __repr__(self):
        return f"<TextModel(id={self.id}, pdf_id={self.pdf_id})>"


class ParsedTextModel(Base):
    """Model for parsed job descriptions."""

    __tablename__ = "parsed_texts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_description_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("job_descriptions.id"),
        nullable=False,
    )
    parsed_text: Mapped[Text] = mapped_column(Text, nullable=False)

    job_description = relationship("JobDescriptionModel", back_populates="parsed_text")
