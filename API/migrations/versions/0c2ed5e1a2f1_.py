"""empty message

Revision ID: 0c2ed5e1a2f1
Revises: a21bb900e85b
Create Date: 2024-02-17 22:59:29.139777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c2ed5e1a2f1'
down_revision = 'a21bb900e85b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('discord_id', sa.BigInteger(), nullable=True))
    op.create_index(op.f('ix_users_discord_id'), 'users', ['discord_id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_discord_id'), table_name='users')
    op.drop_column('users', 'discord_id')
    # ### end Alembic commands ###