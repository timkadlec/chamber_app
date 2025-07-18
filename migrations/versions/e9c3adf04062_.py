"""empty message

Revision ID: e9c3adf04062
Revises: b86ca3e229f2
Create Date: 2024-10-27 18:17:13.119021

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e9c3adf04062'
down_revision = 'b86ca3e229f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('compositions', schema=None) as batch_op:
        batch_op.drop_index('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('compositions', schema=None) as batch_op:
        batch_op.create_index('name', ['name'], unique=True)

    # ### end Alembic commands ###
