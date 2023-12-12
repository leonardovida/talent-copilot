from datetime import datetime

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime

from cv_copilot.db.base import Base

class ScoreModel(Base):

    """Model for Scores."""

    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pdf_id: Mapped[int] = mapped_column(Integer, ForeignKey("pdfs.id"), nullable=False)
    job_description_id: Mapped[int] = mapped_column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    parsed_job_description_id: Mapped[int] = mapped_column(Integer, ForeignKey("parsed_job_descriptions.id"), nullable=False)
    score: Mapped[float] = mapped_column(nullable=False)
    created_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    pdfs = relationship("PDFModel", back_populates="scores")
    job_descriptions = relationship("JobDescriptionModel", back_populates="scores")
    parsed_job_descriptions = relationship("ParsedJobDescriptionModel", back_populates="scores")