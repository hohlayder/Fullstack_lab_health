from uuid import UUID

from fastapi import APIRouter, Response

from app.api.dependencies import Pagination, SessionDep
from app.schemas.health import MedicationCreate, MedicationRead, MedicationUpdate
from app.services import medications
from app.services.common import delete

router = APIRouter(prefix="/medications", tags=["Назначения"])


@router.get("", response_model=list[MedicationRead])
def list_medications(
    session: SessionDep,
    page: Pagination,
    family_id: UUID | None = None,
    member_id: UUID | None = None,
):
    return medications.list_medications(session, family_id, member_id, *page)


@router.post("", response_model=MedicationRead, status_code=201)
def create_medication(payload: MedicationCreate, response: Response, session: SessionDep):
    medication = medications.create_medication(session, payload)
    response.headers["Location"] = f"/api/v1/medications/{medication.id}"
    return medication


@router.get("/{medication_id}", response_model=MedicationRead)
def get_medication(medication_id: UUID, session: SessionDep):
    return medications.get_medication(session, medication_id)


@router.patch("/{medication_id}", response_model=MedicationRead)
def update_medication(medication_id: UUID, payload: MedicationUpdate, session: SessionDep):
    return medications.update_medication(session, medication_id, payload)


@router.delete("/{medication_id}", status_code=204)
def delete_medication(medication_id: UUID, session: SessionDep):
    delete(session, medications.get_medication(session, medication_id))
    return Response(status_code=204)
