from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cv_copilot.db.base import Base


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
    created_date = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    job_description = relationship("JobDescriptionModel", back_populates="parsed_text")
