"""Rename video_id to host_id

Revision ID: b16051dab938
Revises: ac7592c40606
Create Date: 2025-02-04 20:04:20.104676

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b16051dab938'
down_revision: Union[str, None] = 'ac7592c40606'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('comments', 'video_id', new_column_name='host_id')
    op.alter_column('likes', 'video_id', new_column_name='host_id')


def downgrade() -> None:
    op.alter_column('comments', 'host_id', new_column_name='video_id')
    op.alter_column('likes', 'host_id', new_column_name='video_id')
