from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FamilyMember
from app.schemas.health import MemberCreate, MemberUpdate
from app.services.common import get_or_404, save
from app.services.families import get_family


def get_member(session: Session, member_id: UUID) -> FamilyMember:
    return get_or_404(session, FamilyMember, member_id, "Член семьи")


def list_members(
    session: Session, family_id: UUID | None, offset: int, limit: int
) -> list[FamilyMember]:
    query = select(FamilyMember).order_by(FamilyMember.full_name, FamilyMember.id)
    if family_id is not None:
        get_family(session, family_id)
        query = query.where(FamilyMember.family_id == family_id)
    return list(session.scalars(query.offset(offset).limit(limit)))


def create_member(session: Session, payload: MemberCreate) -> FamilyMember:
    get_family(session, payload.family_id)
    return save(session, FamilyMember(**payload.model_dump()))


def update_member(session: Session, member_id: UUID, payload: MemberUpdate) -> FamilyMember:
    member = get_member(session, member_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(member, field, value)
    return save(session, member)
