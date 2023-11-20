from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
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
    created_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)