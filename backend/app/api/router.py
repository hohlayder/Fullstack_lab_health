from datetime import date
from uuid import UUID

from fastapi import APIRouter

from app.api.dependencies import SessionDep
from app.api.routes import families, intakes, medications, members
from app.schemas.health import ScheduleItem
from app.services.views import schedule

api_router = APIRouter(prefix="/api/v1")
for router in (families.router, members.router, medications.router, intakes.router):
    api_router.include_router(router)


@api_router.get("/schedule", response_model=list[ScheduleItem], tags=["Расписание"])
def get_schedule(
    family_id: UUID,
    day: date,
    session: SessionDep,
    member_id: UUID | None = None,
    taken: bool | None = None,
):
    return schedule(session, family_id, member_id, day, taken)
