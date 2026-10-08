from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Family
from app.schemas.health import FamilyCreate, FamilyUpdate
from app.services.common import get_or_404, save


def get_family(session: Session, family_id: UUID) -> Family:
    return get_or_404(session, Family, family_id, "Семья")


def list_families(session: Session, offset: int, limit: int) -> list[Family]:
    return list(
        session.scalars(select(Family).order_by(Family.name, Family.id).offset(offset).limit(limit))
    )


def create_family(session: Session, payload: FamilyCreate) -> Family:
    return save(session, Family(**payload.model_dump()))


def update_family(session: Session, family_id: UUID, payload: FamilyUpdate) -> Family:
    family = get_family(session, family_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(family, field, value)
    return save(session, family)
