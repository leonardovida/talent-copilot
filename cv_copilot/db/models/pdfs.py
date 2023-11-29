from datetime import datetime

from pydantic.networks import HttpUrl
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime, Integer, String

from cv_copilot.db.base import Base


class PDFModel(Base):
    """Model for PDFs."""

    __tablename__ = "pdfs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(length=200),  # noqa: WPS432
        nullable=False,
    )
    job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("job_descriptions.id"),
        nullable=False,
    )
    created_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    file: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    s3_url: Mapped[HttpUrl] = mapped_column(
        String(length=2000),  # noqa: WPS432
        nullable=True,
    )

    job_description = relationship(
        "JobDescriptionModel",
        back_populates="pdfs",
    )
    images = relationship("ImageModel", back_populates="pdf")
    text = relationship("TextModel", back_populates="pdf")
