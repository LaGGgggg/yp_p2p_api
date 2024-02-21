"""empty message

Revision ID: a930d03d907d
Revises: 0c2ed5e1a2f1
Create Date: 2024-02-21 16:00:48.825391

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a930d03d907d'
down_revision = '0c2ed5e1a2f1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('scopes', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('users', 'username',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('users', 'hashed_password',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('users', 'discord_id',
               existing_type=sa.BIGINT(),
               nullable=False)
    op.alter_column('users_to_scopes', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('users_to_scopes', 'scope_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users_to_scopes', 'scope_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('users_to_scopes', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('users', 'discord_id',
               existing_type=sa.BIGINT(),
               nullable=True)
    op.alter_column('users', 'hashed_password',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('users', 'username',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('scopes', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###