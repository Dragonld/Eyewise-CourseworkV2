"""empty message

Revision ID: bb925431fed5
Revises: 1504e866d914
Create Date: 2018-06-18 10:10:48.076335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb925431fed5'
down_revision = '1504e866d914'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_optom_there_day'), 'optom_there', ['day'], unique=False)
    op.create_index(op.f('ix_optom_there_month'), 'optom_there', ['month'], unique=False)
    op.create_index(op.f('ix_optom_there_year'), 'optom_there', ['year'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_optom_there_year'), table_name='optom_there')
    op.drop_index(op.f('ix_optom_there_month'), table_name='optom_there')
    op.drop_index(op.f('ix_optom_there_day'), table_name='optom_there')
    # ### end Alembic commands ###
