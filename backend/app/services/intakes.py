from datetime import date, datetime, time, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FamilyMember, Intake, Medication
from app.schemas.health import IntakeCreate, IntakeUpdate
from app.services.common import get_or_404, save
from app.services.families import get_family
from app.services.medications import get_medication
from app.services.members import get_member


def get_intake(session: Session, intake_id: UUID) -> Intake:
    return get_or_404(session, Intake, intake_id, "Отметка приёма")


def list_intakes(
    session: Session,
    family_id: UUID | None,
    member_id: UUID | None,
    medication_id: UUID | None,
    day: date | None,
    offset: int,
    limit: int,
) -> list[Intake]:
    if family_id is not None:
        get_family(session, family_id)
    if member_id is not None:
        member = get_member(session, member_id)
        if family_id is not None and member.family_id != family_id:
            raise HTTPException(422, "Член семьи не принадлежит выбранной семье")
    if medication_id is not None:
        medication = get_medication(session, medication_id)
        if member_id is not None and medication.member_id != member_id:
            raise HTTPException(422, "Назначение не принадлежит выбранному человеку")
        if family_id is not None and medication.member.family_id != family_id:
            raise HTTPException(422, "Назначение не принадлежит выбранной семье")
    query = select(Intake).join(Medication).join(FamilyMember)
    if family_id is not None:
        query = query.where(FamilyMember.family_id == family_id)
    if member_id is not None:
        query = query.where(Medication.member_id == member_id)
    if medication_id is not None:
        query = query.where(Intake.medication_id == medication_id)
    if day is not None:
        query = query.where(Intake.scheduled_date == day)
    query = query.order_by(Intake.scheduled_date, Intake.scheduled_time, Intake.id)
    return list(session.scalars(query.offset(offset).limit(limit)))


def validate_slot(medication: Medication, day: date, scheduled_time: time, taken: bool) -> None:
    if day < medication.start_date or (
        medication.end_date is not None and day > medication.end_date
    ):
        raise HTTPException(422, "Дата приёма находится вне курса назначения")
    if scheduled_time not in medication.times:
        raise HTTPException(422, "Время приёма отсутствует в расписании назначения")
    if taken and day > date.today():
        raise HTTPException(422, "Нельзя отметить как принятый приём за будущий день")


def create_intake(session: Session, payload: IntakeCreate) -> Intake:
    medication = get_medication(session, payload.medication_id)
    validate_slot(medication, payload.scheduled_date, payload.scheduled_time, payload.taken)
    intake = Intake(
        **payload.model_dump(), taken_at=datetime.now(timezone.utc) if payload.taken else None
    )
    return save(session, intake)


def update_intake(session: Session, intake_id: UUID, payload: IntakeUpdate) -> Intake:
    intake = get_intake(session, intake_id)
    changes = payload.model_dump(exclude_unset=True)
    day = changes.get("scheduled_date", intake.scheduled_date)
    scheduled_time = changes.get("scheduled_time", intake.scheduled_time)
    taken = changes.get("taken", intake.taken)
    validate_slot(intake.medication, day, scheduled_time, taken)
    for field, value in changes.items():
        setattr(intake, field, value)
    if not taken:
        intake.taken_at = None
    elif intake.taken_at is None:
        intake.taken_at = datetime.now(timezone.utc)
    return save(session, intake)
