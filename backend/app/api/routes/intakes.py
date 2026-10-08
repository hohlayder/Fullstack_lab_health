from datetime import date
from uuid import UUID

from fastapi import APIRouter, Response

from app.api.dependencies import Pagination, SessionDep
from app.schemas.health import IntakeCreate, IntakeRead, IntakeUpdate
from app.services import intakes
from app.services.common import delete

router = APIRouter(prefix="/intakes", tags=["Отметки приёма"])


@router.get("", response_model=list[IntakeRead])
def list_intakes(
    session: SessionDep,
    page: Pagination,
    family_id: UUID | None = None,
    member_id: UUID | None = None,
    medication_id: UUID | None = None,
    day: date | None = None,
):
    return intakes.list_intakes(session, family_id, member_id, medication_id, day, *page)


@router.post("", response_model=IntakeRead, status_code=201)
def create_intake(payload: IntakeCreate, response: Response, session: SessionDep):
    intake = intakes.create_intake(session, payload)
    response.headers["Location"] = f"/api/v1/intakes/{intake.id}"
    return intake


@router.get("/{intake_id}", response_model=IntakeRead)
def get_intake(intake_id: UUID, session: SessionDep):
    return intakes.get_intake(session, intake_id)


@router.patch("/{intake_id}", response_model=IntakeRead)
def update_intake(intake_id: UUID, payload: IntakeUpdate, session: SessionDep):
    return intakes.update_intake(session, intake_id, payload)


@router.delete("/{intake_id}", status_code=204)
def delete_intake(intake_id: UUID, session: SessionDep):
    delete(session, intakes.get_intake(session, intake_id))
    return Response(status_code=204)
