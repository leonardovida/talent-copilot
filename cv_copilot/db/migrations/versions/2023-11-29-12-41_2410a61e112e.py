"""empty message

Revision ID: 2410a61e112e
Revises: 58d7d9b60440
Create Date: 2023-11-29 12:41:17.898336

"""
from alembic import op
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import BYTEA, JSONB, UUID
from sqlalchemy.sql.schema import ForeignKey

# revision identifiers, used by Alembic.
revision = "2410a61e112e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create job_descriptions table
    op.create_table(
        "job_descriptions",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("title", String(length=1000), nullable=False),
        Column("description", Text, nullable=False),
        Column("created_date", DateTime, nullable=False),
        Column("updated_date", DateTime, nullable=True),
    )

    # Create pdfs table
    op.create_table(
        "pdfs",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("name", String(length=200), nullable=False),
        Column(
            "job_id",
            Integer,
            ForeignKey("job_descriptions.id"),
            nullable=False,
        ),
        Column("file", BYTEA, nullable=True),
        Column("s3_url", String(length=2000), nullable=True),
        Column("created_date", DateTime, nullable=False),
    )

    # Create images table
    op.create_table(
        "images",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("pdf_id", Integer, ForeignKey("pdfs.id"), nullable=False),
        Column(
            "job_id",
            Integer,
            ForeignKey("job_descriptions.id"),
            nullable=False,
        ),
        Column("encoded_image", Text, nullable=False),
        Column("created_date", DateTime, nullable=False),
    )

    # Create users table
    op.create_table(
        "users",
        Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            default=text("gen_random_uuid()"),
        ),
        Column("email", String(length=255), nullable=False, unique=True),
        Column("hashed_password", String(length=255), nullable=False),
        Column(
            "is_active",
            Boolean(),
            nullable=False,
            server_default=text("TRUE"),
        ),
        Column(
            "is_superuser",
            Boolean(),
            nullable=False,
            server_default=text("FALSE"),
        ),
    )
    op.create_table(
        "texts",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("pdf_id", Integer, ForeignKey("pdfs.id"), nullable=False),
        Column("text", Text, nullable=True),
        Column("created_date", DateTime, nullable=False),
    )
    op.create_table(
        "parsed_texts",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("pdf_id", Integer, nullable=False),
        Column(
            "job_description_id",
            Integer,
            ForeignKey("job_descriptions.id"),
            nullable=False,
        ),
        Column("text_id", Integer, ForeignKey("texts.id"), nullable=False),
        Column("parsed_skills", JSONB, nullable=True),
        Column("created_date", DateTime, nullable=False),
    )
    op.create_table(
        "parsed_job_descriptions",
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column(
            "job_description_id",
            Integer,
            ForeignKey("job_descriptions.id"),
            nullable=False,
        ),
        Column("parsed_skills", JSONB, nullable=True),
        Column("created_date", DateTime, nullable=False),
    )
    op.create_table(
        "scores",
        Column("id", Integer(), primary_key=True, autoincrement=True),
        Column("pdf_id", Integer(), ForeignKey("pdfs.id"), nullable=False),
        Column(
            "job_description_id",
            Integer(),
            ForeignKey("job_descriptions.id"),
            nullable=False,
        ),
        Column(
            "parsed_job_description_id",
            Integer(),
            ForeignKey("parsed_job_descriptions.id"),
            nullable=False,
        ),
        Column("score", Float(), nullable=False),
        Column(
            "created_date",
            DateTime,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
        Column("updated_date", DateTime, nullable=True),
    )
    print("Migration 2410a61e112e applied successfully.")


def downgrade() -> None:
    op.drop_table("parsed_texts")
    op.drop_table("parsed_job_descriptions")
    op.drop_table("images")
    op.drop_table("pdfs")
    op.drop_table("job_descriptions")
    op.drop_table("users")
    op.drop_table("texts")
    op.drop_table("scores")
