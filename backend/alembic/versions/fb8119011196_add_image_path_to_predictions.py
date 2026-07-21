"""add image_path to predictions

Revision ID: fb8119011196
Revises: 4cd598006a3b
Create Date: 2026-07-21 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb8119011196'
down_revision: Union[str, None] = '4cd598006a3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('predictions', sa.Column('image_path', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('predictions', 'image_path')
