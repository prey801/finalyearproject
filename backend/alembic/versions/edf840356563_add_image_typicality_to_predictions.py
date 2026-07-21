"""add image_typicality to predictions

Revision ID: edf840356563
Revises: fb8119011196
Create Date: 2026-07-21 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'edf840356563'
down_revision: Union[str, None] = 'fb8119011196'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('predictions', sa.Column('image_typicality', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('predictions', 'image_typicality')
