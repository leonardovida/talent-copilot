"""empty message

Revision ID: 2410a61e112e
Revises: 58d7d9b60440
Create Date: 2023-11-29 12:41:17.898336

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import BYTEA, UUID
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
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(length=1000), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("created_date", sa.DateTime, nullable=False),
        sa.Column("updated_date", sa.DateTime, nullable=True),
    )

    # Create pdfs table
    op.create_table(
        "pdfs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column(
            "job_id",
            sa.Integer,
            ForeignKey("job_descriptions.id"),
            nullable=False,
        ),
        sa.Column("file", BYTEA, nullable=True),
        sa.Column("s3_url", sa.String(length=2000), nullable=True),
        sa.Column("created_date", sa.DateTime, nullable=False),
    )

    # Create images table
    op.create_table(
        "images",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("pdf_id", sa.Integer, ForeignKey("pdfs.id"), nullable=False),
        sa.Column(
            "job_id",
            sa.Integer,
            ForeignKey("job_descriptions.id"),
            nullable=False,
        ),
        sa.Column("encoded_image", sa.Text, nullable=False),
        sa.Column("text", sa.Text, nullable=True),
        sa.Column("created_date", sa.DateTime, nullable=False),
    )

    # Create users table
    op.create_table(
        "users",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("TRUE"),
        ),
        sa.Column(
            "is_superuser",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("FALSE"),
        ),
    )
    op.create_table(
        "texts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("pdf_id", sa.Integer, ForeignKey("pdfs.id"), nullable=False),
        sa.Column("text", sa.Text, nullable=True),
        sa.Column("created_date", sa.DateTime, nullable=False),
    )
    op.create_table(
        "parsed_texts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "job_description_id",
            sa.Integer,
            ForeignKey("pdfs.id"),
            nullable=False,
        ),
        sa.Column("parsed_text", sa.Text, nullable=True),
        sa.Column("created_date", sa.DateTime, nullable=False),
    )
    op.create_table(
        "parsed_job_descriptions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "job_description_id",
            sa.Integer,
            ForeignKey("pdfs.id"),
            nullable=False,
        ),
        sa.Column("parsed_text", sa.Text, nullable=True),
        sa.Column("created_date", sa.DateTime, nullable=False),
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
