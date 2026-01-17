"""restart_edificio_id_sequence

Revision ID: 11a46bdb5144
Revises: 21eca8faba87
Create Date: 2026-01-17 15:13:18.753234

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11a46bdb5144'
down_revision: Union[str, None] = '21eca8faba87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """
    Reinicia la secuencia de ID de la tabla Edificio para que comience en 319.
    """
    # Reiniciar la secuencia en 319
    op.execute('ALTER SEQUENCE "Edificio_Id_seq" RESTART WITH 319')


def downgrade() -> None:
    pass
