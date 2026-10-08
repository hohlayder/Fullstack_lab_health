from datetime import date
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Intake, Medication
from app.schemas.health import DoctorList, MedicationRead, MemberRead, ScheduleItem
from app.services.medications import medication_query
from app.services.members import get_member


def active_medications(
    session: Session, family_id: UUID, member_id: UUID | None, day: date
) -> list[Medication]:
    query = (
        medication_query(session, family_id, member_id)
        .where(
            Medication.start_date <= day,
            or_(Medication.end_date.is_(None), Medication.end_date >= day),
        )
        .options(joinedload(Medication.member))
        .order_by(Medication.name, Medication.id)
    )
    return list(session.scalars(query))


def schedule(
    session: Session, family_id: UUID, member_id: UUID | None, day: date, taken: bool | None = None
) -> list[ScheduleItem]:
    medications = active_medications(session, family_id, member_id, day)
    medication_ids = [medication.id for medication in medications]
    if not medication_ids:
        return []
    records = session.scalars(
        select(Intake).where(
            Intake.medication_id.in_(medication_ids),
            Intake.scheduled_date == day,
        )
    )
    by_slot = {(record.medication_id, record.scheduled_time): record for record in records}
    result = []
    for medication in medications:
        for scheduled_time in medication.times:
            record = by_slot.get((medication.id, scheduled_time))
            item = ScheduleItem(
                medication_id=medication.id,
                intake_id=record.id if record else None,
                member_id=medication.member_id,
                member_name=medication.member.full_name,
                medication_name=medication.name,
                dose=medication.dose,
                instructions=medication.instructions,
                scheduled_date=day,
                scheduled_time=scheduled_time,
                taken=record.taken if record else False,
                taken_at=record.taken_at if record else None,
            )
            if taken is None or item.taken == taken:
                result.append(item)
    return sorted(
        result, key=lambda item: (item.scheduled_time, item.member_name, str(item.medication_id))
    )


def doctor_list(session: Session, member_id: UUID, day: date) -> DoctorList:
    member = get_member(session, member_id)
    medications = active_medications(session, member.family_id, member.id, day)
    plan = schedule(session, member.family_id, member.id, day)
    return DoctorList(
        day=day,
        member=MemberRead.model_validate(member),
        medications=[MedicationRead.model_validate(medication) for medication in medications],
        scheduled_count=len(plan),
        taken_count=sum(item.taken for item in plan),
    )
