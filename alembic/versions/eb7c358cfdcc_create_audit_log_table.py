"""create_audit_log_table

Revision ID: eb7c358cfdcc
Revises: 34b854e77c73
Create Date: 2026-01-19 11:33:43.202494

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb7c358cfdcc'
down_revision: Union[str, None] = '34b854e77c73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('request_id', sa.String(100), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('method', sa.String(10), nullable=False),
        sa.Column('path', sa.String(500), nullable=False),
        sa.Column('user_id', sa.String(100), nullable=True),
        sa.Column('user_ip', sa.String(50), nullable=True),
        sa.Column('query_params', sa.JSON(), nullable=True),
        sa.Column('path_params', sa.JSON(), nullable=True),
        sa.Column('request_body', sa.JSON(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('response_body', sa.JSON(), nullable=True),
        sa.Column('duration_ms', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_traceback', sa.Text(), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('endpoint', sa.String(200), nullable=True),
    )

    # Índices para mejorar queries
    op.create_index('ix_audit_log_request_id', 'audit_log', ['request_id'])
    op.create_index('ix_audit_log_timestamp', 'audit_log', ['timestamp'])
    op.create_index('ix_audit_log_path', 'audit_log', ['path'])
    op.create_index('ix_audit_log_user_id', 'audit_log', ['user_id'])


def downgrade():
    op.drop_table('audit_log')
