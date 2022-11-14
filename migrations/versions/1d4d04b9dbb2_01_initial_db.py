"""01_initial-db

Revision ID: 1d4d04b9dbb2
Revises: 
Create Date: 2022-11-10 23:19:10.630456

"""
import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op


# revision identifiers, used by Alembic.
revision = '1d4d04b9dbb2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('short_urls',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('origin_url', sqlalchemy_utils.types.url.URLType(), nullable=False),
    sa.Column('short_url', sqlalchemy_utils.types.url.URLType(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('short_form', sa.String(length=6), nullable=False),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_short_urls_created_at'), 'short_urls', ['created_at'], unique=False)
    op.create_table('requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url_id', sa.Integer(), nullable=True),
    sa.Column('made_at', sa.DateTime(), nullable=True),
    sa.Column('client_host', sa.String(), nullable=False),
    sa.Column('client_port', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['url_id'], ['short_urls.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_requests_made_at'), 'requests', ['made_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_requests_made_at'), table_name='requests')
    op.drop_table('requests')
    op.drop_index(op.f('ix_short_urls_created_at'), table_name='short_urls')
    op.drop_table('short_urls')
    # ### end Alembic commands ###