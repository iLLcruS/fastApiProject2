"""Initial

Revision ID: 84c05025a98c
Revises: aacfe1f6c7cf
Create Date: 2023-12-09 03:11:22.343478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84c05025a98c'
down_revision: Union[str, None] = 'aacfe1f6c7cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('logger', sa.Column('log_email_user', sa.String(), nullable=True))
    op.create_foreign_key(None, 'logger', 'user', ['log_email_user'], ['email'])
    op.drop_column('logger', 'log_name_user')
    op.create_unique_constraint(None, 'user', ['username'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='unique')
    op.add_column('logger', sa.Column('log_name_user', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'logger', type_='foreignkey')
    op.drop_column('logger', 'log_email_user')
    # ### end Alembic commands ###
