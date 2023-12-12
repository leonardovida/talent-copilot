from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cv_copilot.db.base import Base


class TextModel(Base):
    """Model for Texts."""

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
    parsed_text = relationship("ParsedTextModel")


class ParsedTextModel(Base):
    """Model for the match between the Job description and the CV."""

    __tablename__ = "parsed_texts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_description_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("job_descriptions.id"),
        nullable=False,
    )
    text_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("texts.id"),
        nullable=False,
    )
    pdf_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    parsed_skills: Mapped[JSONB] = mapped_column(JSONB, nullable=False)
    created_date = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    job_description = relationship("JobDescriptionModel", back_populates="parsed_text")
    text = relationship("TextModel", back_populates="parsed_text")
