"""event and bet tables

Revision ID: 4658519f53b6
Revises:
Create Date: 2024-11-28 20:43:17.208537

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4658519f53b6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "event",
        sa.Column("coefficient", sa.Float(), nullable=True),
        sa.Column("deadline", sa.Integer(), nullable=True),
        sa.Column(
            "state",
            sa.Enum("NEW", "FINISHED_WIN", "FINISHED_LOSE", name="eventstate"),
            nullable=True,
        ),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_table(
        "bet",
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("bet_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["event.event_id"],
        ),
        sa.PrimaryKeyConstraint("bet_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("bet")
    op.drop_table("event")
    # ### end Alembic commands ###
