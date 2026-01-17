"""restart_provincia_id_sequence

Revision ID: 21eca8faba87
Revises: 705c50bcf060
Create Date: 2026-01-17 14:59:32.786488

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21eca8faba87'
down_revision: Union[str, None] = '705c50bcf060'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Reiniciar la secuencia en 3
    op.execute("ALTER SEQUENCE \"Provincia_Id_seq\" RESTART WITH 26")

def downgrade():
    # Opcional: volver al valor anterior
    op.execute("ALTER SEQUENCE \"Provincia_Id_seq\" RESTART WITH 25")
