"""fix photo_tag_association

Revision ID: 5dd44bbc323b
Revises: 37747b16d397
Create Date: 2024-10-12 23:10:53.278557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5dd44bbc323b'
down_revision: Union[str, None] = '37747b16d397'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('photo_tag_association_tag_id_fkey', 'photo_tag_association', type_='foreignkey')
    op.drop_constraint('photo_tag_association_photo_id_fkey', 'photo_tag_association', type_='foreignkey')
    op.create_foreign_key(None, 'photo_tag_association', 'photos', ['photo_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'photo_tag_association', 'tags', ['tag_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'photo_tag_association', type_='foreignkey')
    op.drop_constraint(None, 'photo_tag_association', type_='foreignkey')
    op.create_foreign_key('photo_tag_association_photo_id_fkey', 'photo_tag_association', 'photos', ['photo_id'], ['id'])
    op.create_foreign_key('photo_tag_association_tag_id_fkey', 'photo_tag_association', 'tags', ['tag_id'], ['id'])
    # ### end Alembic commands ###
