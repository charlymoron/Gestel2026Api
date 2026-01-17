"""restart_dominio_id_sequence

Revision ID: 1e2f41585072
Revises: 11a46bdb5144
Create Date: 2026-01-17 16:12:00.320545

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e2f41585072'
down_revision: Union[str, None] = '11a46bdb5144'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Reiniciar la secuencia en 319
    op.execute('ALTER SEQUENCE "Dominio_Id_seq" RESTART WITH 9')


def downgrade() -> None:
    pass
