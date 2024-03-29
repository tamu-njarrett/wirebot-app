"""Addding row number to Status

Revision ID: 485f22281063
Revises: 98aa72aad4a2
Create Date: 2023-04-20 13:29:29.864260

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '485f22281063'
down_revision = '98aa72aad4a2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('status', schema=None) as batch_op:
        batch_op.add_column(sa.Column('row_num', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('status', schema=None) as batch_op:
        batch_op.drop_column('row_num')

    # ### end Alembic commands ###
