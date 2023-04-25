"""Change run time to time object

Revision ID: 98aa72aad4a2
Revises: 422c1dc43fad
Create Date: 2023-04-20 01:37:38.688762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98aa72aad4a2'
down_revision = '422c1dc43fad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('run_time', schema=None) as batch_op:
        batch_op.alter_column('run_time',
               existing_type=sa.INTEGER(),
               type_=sa.Time(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('run_time', schema=None) as batch_op:
        batch_op.alter_column('run_time',
               existing_type=sa.Time(),
               type_=sa.INTEGER(),
               existing_nullable=True)

    # ### end Alembic commands ###
