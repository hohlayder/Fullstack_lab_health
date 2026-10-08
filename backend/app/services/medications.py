from datetime import date, time
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import FamilyMember, Intake, Medication, MedicationTime
from app.schemas.health import MedicationCreate, MedicationUpdate
from app.services.common import get_or_404, save
from app.services.families import get_family
from app.services.members import get_member


def get_medication(session: Session, medication_id: UUID) -> Medication:
    return get_or_404(session, Medication, medication_id, "Назначение")


def medication_query(session: Session, family_id: UUID | None, member_id: UUID | None):
    if family_id is not None:
        get_family(session, family_id)
    if member_id is not None:
        member = get_member(session, member_id)
        if family_id is not None and member.family_id != family_id:
            raise HTTPException(422, "Член семьи не принадлежит выбранной семье")
    query = select(Medication).join(FamilyMember)
    if family_id is not None:
        query = query.where(FamilyMember.family_id == family_id)
    if member_id is not None:
        query = query.where(Medication.member_id == member_id)
    return query


def list_medications(
    session: Session, family_id: UUID | None, member_id: UUID | None, offset: int, limit: int
) -> list[Medication]:
    query = medication_query(session, family_id, member_id).order_by(Medication.name, Medication.id)
    return list(session.scalars(query.offset(offset).limit(limit)))


def set_times(medication: Medication, times: list[time]) -> None:
    existing = {item.time: item for item in medication.dose_times}
    medication.dose_times = [
        existing[value] if value in existing else MedicationTime(time=value) for value in times
    ]


def create_medication(session: Session, payload: MedicationCreate) -> Medication:
    get_member(session, payload.member_id)
    medication = Medication(**payload.model_dump(exclude={"times"}))
    set_times(medication, payload.times)
    return save(session, medication)


def update_medication(
    session: Session, medication_id: UUID, payload: MedicationUpdate
) -> Medication:
    medication = get_medication(session, medication_id)
    changes = payload.model_dump(exclude_unset=True)
    start_date: date = changes.get("start_date", medication.start_date)
    end_date: date | None = changes.get("end_date", medication.end_date)
    times: list[time] = changes.get("times", medication.times)
    if end_date is not None and end_date < start_date:
        raise HTTPException(422, "Конец курса не может быть раньше начала")
    if changes.keys() & {"start_date", "end_date", "times"}:
        invalid = [Intake.scheduled_date < start_date, Intake.scheduled_time.not_in(times)]
        if end_date is not None:
            invalid.append(Intake.scheduled_date > end_date)
        conflict = session.scalar(
            select(Intake.id).where(Intake.medication_id == medication.id, or_(*invalid)).limit(1)
        )
        if conflict is not None:
            raise HTTPException(409, "Новое расписание противоречит существующим отметкам приёма")
    for field, value in changes.items():
        if field == "times":
            set_times(medication, value)
        else:
            setattr(medication, field, value)
    return save(session, medication)
