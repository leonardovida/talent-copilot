"""empty message

Revision ID: cf8ebb9bba84
Revises: 819cbf6e030b
Create Date: 2023-11-26 10:44:34.210235

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import BYTEA, UUID
from sqlalchemy.sql.schema import ForeignKey

# revision identifiers, used by Alembic.
revision = "cf8ebb9bba84"
down_revision = "819cbf6e030b"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
        sa.Column("created_date", sa.DateTime, nullable=False),
        sa.Column("file", BYTEA, nullable=True),
        sa.Column("s3_url", sa.String(length=2000), nullable=True),
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
        # Add other user columns here, such as first_name, last_name, etc.
    )


def downgrade() -> None:
    op.drop_table("images")
    op.drop_table("pdfs")
    op.drop_table("job_descriptions")
    op.drop_table("users")
