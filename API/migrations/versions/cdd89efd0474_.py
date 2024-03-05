"""empty message

Revision ID: cdd89efd0474
Revises: 5ea3d3527a03
Create Date: 2024-02-29 14:52:10.166513

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cdd89efd0474'
down_revision = '5ea3d3527a03'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('p2p_requests', sa.Column('review_start_date', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('p2p_requests', 'review_start_date')
    # ### end Alembic commands ###