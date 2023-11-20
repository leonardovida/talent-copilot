from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Integer, Text

from cv_copilot.db.base import Base


class ImageModel(Base):
    """Model for storage of Images.

    The images are single pages of a PDF that have been extracted and encoded as base64 strings.
    """

    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pdf_id: Mapped[int] = mapped_column(Integer, ForeignKey("pdfs.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("job_descriptions.id"),
        nullable=False,
    )
    encoded_image: Mapped[str] = mapped_column(
        Text,  # Using Text type for base64 encoded image
        nullable=False,
    )
    text: Mapped[str] = mapped_column(
        Text,  # Using Text type for extracted text
        nullable=True,  # Initially nullable, will be populated later
    )

    # Relationship to the PDFModel (if needed)
    pdf = relationship("PDFModel", back_populates="images")
    job_description = relationship("JobDescriptionModel", back_populates="images")
