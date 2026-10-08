from datetime import date
from uuid import UUID

from fastapi import APIRouter, Response

from app.api.dependencies import Pagination, SessionDep
from app.schemas.health import DoctorList, MemberCreate, MemberRead, MemberUpdate
from app.services import members, views
from app.services.common import delete

router = APIRouter(prefix="/members", tags=["Члены семьи"])


@router.get("", response_model=list[MemberRead])
def list_members(session: SessionDep, page: Pagination, family_id: UUID | None = None):
    return members.list_members(session, family_id, *page)


@router.post("", response_model=MemberRead, status_code=201)
def create_member(payload: MemberCreate, response: Response, session: SessionDep):
    member = members.create_member(session, payload)
    response.headers["Location"] = f"/api/v1/members/{member.id}"
    return member


@router.get("/{member_id}", response_model=MemberRead)
def get_member(member_id: UUID, session: SessionDep):
    return members.get_member(session, member_id)


@router.patch("/{member_id}", response_model=MemberRead)
def update_member(member_id: UUID, payload: MemberUpdate, session: SessionDep):
    return members.update_member(session, member_id, payload)


@router.delete("/{member_id}", status_code=204)
def delete_member(member_id: UUID, session: SessionDep):
    delete(session, members.get_member(session, member_id))
    return Response(status_code=204)


@router.get("/{member_id}/doctor-list", response_model=DoctorList)
def get_doctor_list(member_id: UUID, day: date, session: SessionDep):
    return views.doctor_list(session, member_id, day)
