from datetime import datetime

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime, String, Text

from cv_copilot.db.base import Base


class JobDescriptionModel(Base):
    """Model for Job Descriptions."""

    __tablename__ = "job_descriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(
        String(length=1000),  # noqa: WPS432
        nullable=False,
    )
    description: Mapped[Text] = mapped_column(Text, nullable=False)
    created_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    pdfs = relationship("PDFModel", cascade="all, delete-orphan")
    images = relationship("ImageModel", cascade="all, delete-orphan")
    parsed_job_description = relationship(
        "ParsedJobDescriptionModel",
        cascade="all, delete-orphan",
    )
    parsed_text = relationship("ParsedTextModel", cascade="all, delete-orphan")
    scores = relationship("ScoreModel", cascade="all, delete-orphan")


class ParsedJobDescriptionModel(Base):
    """Model for parsed job descriptions."""

    __tablename__ = "parsed_job_descriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_description_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("job_descriptions.id"),
        nullable=False,
    )
    parsed_skills: Mapped[JSONB] = mapped_column(JSONB, nullable=False)
    created_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    job_description = relationship(
        "JobDescriptionModel",
        back_populates="parsed_job_description",
    )
    scores = relationship("ScoreModel", cascade="all, delete-orphan")
