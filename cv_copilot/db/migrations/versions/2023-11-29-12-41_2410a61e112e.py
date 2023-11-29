"""empty message

Revision ID: 2410a61e112e
Revises: 58d7d9b60440
Create Date: 2023-11-29 12:41:17.898336

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.schema import ForeignKey

# revision identifiers, used by Alembic.
revision = "2410a61e112e"
down_revision = "58d7d9b60440"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
    )


def downgrade() -> None:
    op.drop_table("parsed_texts")
    op.drop_table("parsed_job_descriptions")
