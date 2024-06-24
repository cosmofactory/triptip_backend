"""20240622132611

Revision ID: 70d03c7f4462
Revises: 868d5a60fdd4
Create Date: 2024-06-22 13:26:11.771350

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "70d03c7f4462"
down_revision: Union[str, None] = "868d5a60fdd4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f("ix_locations_updated_at"), "locations", ["updated_at"], unique=False)
    op.create_index(
        op.f("ix_refresh_tokens_updated_at"), "refresh_tokens", ["updated_at"], unique=False
    )
    op.create_index(op.f("ix_trips_updated_at"), "trips", ["updated_at"], unique=False)
    op.create_index(op.f("ix_users_updated_at"), "users", ["updated_at"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_users_updated_at"), table_name="users")
    op.drop_index(op.f("ix_trips_updated_at"), table_name="trips")
    op.drop_index(op.f("ix_refresh_tokens_updated_at"), table_name="refresh_tokens")
    op.drop_index(op.f("ix_locations_updated_at"), table_name="locations")
    # ### end Alembic commands ###