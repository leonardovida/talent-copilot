from sqlalchemy.orm import DeclarativeBase

from cv_copilot.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
