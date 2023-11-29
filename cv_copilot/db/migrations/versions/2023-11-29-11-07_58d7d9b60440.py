"""empty message

Revision ID: 58d7d9b60440
Revises: cf8ebb9bba84
Create Date: 2023-11-29 11:07:38.578436

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.schema import ForeignKey

# revision identifiers, used by Alembic.
revision = "58d7d9b60440"
down_revision = "cf8ebb9bba84"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create texts table
    op.create_table(
        "texts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("pdf_id", sa.Integer, ForeignKey("pdfs.id"), nullable=False),
        sa.Column("text", sa.Text, nullable=True),
    )


def downgrade() -> None:
    # Drop texts table
    op.drop_table("texts")
