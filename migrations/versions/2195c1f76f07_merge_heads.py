"""Merge heads

Revision ID: 2195c1f76f07
Revises: add_location_final_20250802, fix_alerts_production_columns
Create Date: 2025-08-06 11:42:14.183192

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2195c1f76f07'
down_revision = ('add_location_final_20250802', 'fix_alerts_production_columns')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
