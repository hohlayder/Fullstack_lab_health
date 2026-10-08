from datetime import date, datetime, time
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Family(Base):
    __tablename__ = "families"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120))
    members: Mapped[list["FamilyMember"]] = relationship(
        back_populates="family", cascade="all, delete-orphan", passive_deletes=True
    )


class FamilyMember(Base):
    __tablename__ = "family_members"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    family_id: Mapped[UUID] = mapped_column(
        ForeignKey("families.id", ondelete="CASCADE"), index=True
    )
    full_name: Mapped[str] = mapped_column(String(160))
    birth_date: Mapped[date] = mapped_column(Date)
    relation: Mapped[str] = mapped_column(String(50))
    family: Mapped[Family] = relationship(back_populates="members")
    medications: Mapped[list["Medication"]] = relationship(
        back_populates="member", cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def first_name(self) -> str:
        return self.full_name.split()[0]

    @property
    def age(self) -> int:
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )


class Medication(Base):
    __tablename__ = "medications"
    __table_args__ = (
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="course_dates"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    member_id: Mapped[UUID] = mapped_column(
        ForeignKey("family_members.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(120))
    form: Mapped[str] = mapped_column(String(80))
    dose: Mapped[str] = mapped_column(String(120))
    instructions: Mapped[str] = mapped_column(Text, default="")
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    member: Mapped[FamilyMember] = relationship(back_populates="medications")
    dose_times: Mapped[list["MedicationTime"]] = relationship(
        back_populates="medication",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="MedicationTime.time",
        lazy="selectin",
    )
    intakes: Mapped[list["Intake"]] = relationship(
        back_populates="medication", cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def times(self) -> list[time]:
        return sorted(dose_time.time for dose_time in self.dose_times)


class MedicationTime(Base):
    __tablename__ = "medication_times"

    medication_id: Mapped[UUID] = mapped_column(
        ForeignKey("medications.id", ondelete="CASCADE"), primary_key=True
    )
    time: Mapped[time] = mapped_column(Time, primary_key=True)
    medication: Mapped[Medication] = relationship(back_populates="dose_times")


class Intake(Base):
    __tablename__ = "intakes"
    __table_args__ = (
        UniqueConstraint(
            "medication_id", "scheduled_date", "scheduled_time", name="uq_intake_slot"
        ),
        CheckConstraint(
            "(taken AND taken_at IS NOT NULL) OR (NOT taken AND taken_at IS NULL)",
            name="taken_timestamp",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    medication_id: Mapped[UUID] = mapped_column(
        ForeignKey("medications.id", ondelete="CASCADE"), index=True
    )
    scheduled_date: Mapped[date] = mapped_column(Date, index=True)
    scheduled_time: Mapped[time] = mapped_column(Time)
    taken: Mapped[bool] = mapped_column(default=False)
    taken_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    medication: Mapped[Medication] = relationship(back_populates="intakes")
