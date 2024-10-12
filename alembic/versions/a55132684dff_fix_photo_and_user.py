"""fix photo and user

Revision ID: a55132684dff
Revises: ce12dde22c5f
Create Date: 2024-10-12 13:37:41.172923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a55132684dff'
down_revision: Union[str, None] = 'ce12dde22c5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('photos_user_id_fkey', 'photos', type_='foreignkey')
    op.create_foreign_key(None, 'photos', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'photos', type_='foreignkey')
    op.create_foreign_key('photos_user_id_fkey', 'photos', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###
