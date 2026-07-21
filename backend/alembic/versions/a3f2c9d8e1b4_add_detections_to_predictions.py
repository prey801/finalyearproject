"""add detections to predictions

Revision ID: a3f2c9d8e1b4
Revises: edf840356563
Create Date: 2026-07-21 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f2c9d8e1b4'
down_revision: Union[str, None] = 'edf840356563'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('predictions', sa.Column('detections', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('predictions', 'detections')
