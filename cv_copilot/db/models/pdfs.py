from pydantic.networks import HttpUrl
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Mapped, mapped_column
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
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"), nullable=False)
    uploaded_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    file: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    s3_url: Mapped[HttpUrl] = mapped_column(
        String(length=2000),  # noqa: WPS432
        nullable=True,
    )
