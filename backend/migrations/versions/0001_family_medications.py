"""Create families, members, medications, schedule times and intake records."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "families",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_families"),
    )
    op.create_table(
        "family_members",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("family_id", sa.Uuid(), nullable=False),
        sa.Column("full_name", sa.String(160), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("relation", sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(
            ["family_id"],
            ["families.id"],
            ondelete="CASCADE",
            name="fk_family_members_family_id_families",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_family_members"),
    )
    op.create_index("ix_family_members_family_id", "family_members", ["family_id"])
    op.create_table(
        "medications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("member_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("form", sa.String(80), nullable=False),
        sa.Column("dose", sa.String(120), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.CheckConstraint(
            "end_date IS NULL OR end_date >= start_date", name=op.f("ck_medications_course_dates")
        ),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["family_members.id"],
            ondelete="CASCADE",
            name="fk_medications_member_id_family_members",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_medications"),
    )
    op.create_index("ix_medications_member_id", "medications", ["member_id"])
    op.create_table(
        "medication_times",
        sa.Column("medication_id", sa.Uuid(), nullable=False),
        sa.Column("time", sa.Time(), nullable=False),
        sa.ForeignKeyConstraint(
            ["medication_id"],
            ["medications.id"],
            ondelete="CASCADE",
            name="fk_medication_times_medication_id_medications",
        ),
        sa.PrimaryKeyConstraint("medication_id", "time", name="pk_medication_times"),
    )
    op.create_table(
        "intakes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("medication_id", sa.Uuid(), nullable=False),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column("scheduled_time", sa.Time(), nullable=False),
        sa.Column("taken", sa.Boolean(), nullable=False),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "(taken AND taken_at IS NOT NULL) OR (NOT taken AND taken_at IS NULL)",
            name=op.f("ck_intakes_taken_timestamp"),
        ),
        sa.ForeignKeyConstraint(
            ["medication_id"],
            ["medications.id"],
            ondelete="CASCADE",
            name="fk_intakes_medication_id_medications",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_intakes"),
        sa.UniqueConstraint(
            "medication_id", "scheduled_date", "scheduled_time", name="uq_intake_slot"
        ),
    )
    op.create_index("ix_intakes_medication_id", "intakes", ["medication_id"])
    op.create_index("ix_intakes_scheduled_date", "intakes", ["scheduled_date"])


def downgrade():
    op.drop_table("intakes")
    op.drop_table("medication_times")
    op.drop_table("medications")
    op.drop_table("family_members")
    op.drop_table("families")
