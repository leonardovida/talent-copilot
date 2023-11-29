from datetime import datetime

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime

from cv_copilot.db.base import Base


class ParsedJobDescriptionModel(Base):
    """Model for parsed job descriptions."""

    __tablename__ = "parsed_job_descriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_description_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("job_descriptions.id"),
        nullable=False,
    )
    parsed_text: Mapped[JSONB] = mapped_column(JSONB, nullable=False)
    created_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    job_description = relationship(
        "JobDescriptionModel",
        back_populates="parsed_job_description",
    )
