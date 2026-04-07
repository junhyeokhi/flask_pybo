"""merge multiple heads

Revision ID: b65160764e80
Revises: 684981f1b13d, fb7c20665d76
Create Date: 2026-04-07 10:01:22.354932

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b65160764e80'
down_revision = ('684981f1b13d', 'fb7c20665d76')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
