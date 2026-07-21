"""add processing_time_ms to predictions

Revision ID: 4cd598006a3b
Revises: 76624626c679
Create Date: 2026-07-21 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4cd598006a3b'
down_revision: Union[str, None] = '76624626c679'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('predictions', sa.Column('processing_time_ms', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('predictions', 'processing_time_ms')
