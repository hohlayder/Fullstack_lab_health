from uuid import UUID

from fastapi import APIRouter, Response

from app.api.dependencies import Pagination, SessionDep
from app.schemas.health import FamilyCreate, FamilyRead, FamilyUpdate
from app.services import families
from app.services.common import delete

router = APIRouter(prefix="/families", tags=["Семьи"])


@router.get("", response_model=list[FamilyRead])
def list_families(session: SessionDep, page: Pagination):
    return families.list_families(session, *page)


@router.post("", response_model=FamilyRead, status_code=201)
def create_family(payload: FamilyCreate, response: Response, session: SessionDep):
    family = families.create_family(session, payload)
    response.headers["Location"] = f"/api/v1/families/{family.id}"
    return family


@router.get("/{family_id}", response_model=FamilyRead)
def get_family(family_id: UUID, session: SessionDep):
    return families.get_family(session, family_id)


@router.patch("/{family_id}", response_model=FamilyRead)
def update_family(family_id: UUID, payload: FamilyUpdate, session: SessionDep):
    return families.update_family(session, family_id, payload)


@router.delete("/{family_id}", status_code=204)
def delete_family(family_id: UUID, session: SessionDep):
    delete(session, families.get_family(session, family_id))
    return Response(status_code=204)
