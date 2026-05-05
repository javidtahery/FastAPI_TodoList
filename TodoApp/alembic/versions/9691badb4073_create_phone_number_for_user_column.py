"""Create phone number for user column

Revision ID: 9691badb4073
Revises: 
Create Date: 2026-04-29 17:48:50.417765

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9691badb4073'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('userss', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('userss', 'phone_number')
