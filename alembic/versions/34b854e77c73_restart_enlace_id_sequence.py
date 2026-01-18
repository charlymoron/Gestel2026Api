"""restart_enlace_id_sequence

Revision ID: 34b854e77c73
Revises: 1e2f41585072
Create Date: 2026-01-18 11:17:35.987911

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34b854e77c73'
down_revision: Union[str, None] = '1e2f41585072'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('ALTER SEQUENCE "Enlace_Id_seq" RESTART WITH 319')


def downgrade() -> None:
    pass
