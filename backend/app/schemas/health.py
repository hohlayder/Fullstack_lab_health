from datetime import date, datetime, time
from typing import Annotated, Self
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
Relation = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
Form = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]
Instructions = Annotated[str, StringConstraints(strip_whitespace=True, max_length=2000)]


def validate_time(value: time) -> time:
    if value.tzinfo is not None or value.second or value.microsecond:
        raise ValueError("Укажите местное время с точностью до минуты, например 08:30")
    return value


def validate_times(values: list[time]) -> list[time]:
    for value in values:
        validate_time(value)
    if len(values) != len(set(values)):
        raise ValueError("Время приёма не должно повторяться")
    return sorted(values)


def validate_birth_date(value: date) -> date:
    if value > date.today() or value < date(1900, 1, 1):
        raise ValueError("Дата рождения должна быть между 01.01.1900 и сегодняшним днём")
    return value


class Schema(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


class PatchSchema(Schema):
    @model_validator(mode="after")
    def require_changes(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("Укажите хотя бы одно поле для изменения")
        for field in self.model_fields_set:
            if getattr(self, field) is None and field != "end_date":
                raise ValueError(f"Поле {field} не может быть null")
        return self


class FamilyCreate(Schema):
    name: Name


class FamilyUpdate(PatchSchema):
    name: Name | None = None


class FamilyRead(Schema):
    id: UUID
    name: str


class MemberCreate(Schema):
    family_id: UUID
    full_name: FullName
    birth_date: date
    relation: Relation

    _birth_date = field_validator("birth_date")(validate_birth_date)


class MemberUpdate(PatchSchema):
    full_name: FullName | None = None
    birth_date: date | None = None
    relation: Relation | None = None

    @field_validator("birth_date")
    @classmethod
    def valid_birth_date(cls, value: date | None) -> date | None:
        return validate_birth_date(value) if value is not None else None


class MemberRead(Schema):
    id: UUID
    family_id: UUID
    full_name: str
    first_name: str
    birth_date: date
    age: int
    relation: str


class MedicationCreate(Schema):
    member_id: UUID
    name: Name
    form: Form
    dose: Name
    instructions: Instructions = ""
    start_date: date
    end_date: date | None = None
    times: list[time] = Field(min_length=1, max_length=12)

    _times = field_validator("times")(validate_times)

    @model_validator(mode="after")
    def valid_course(self) -> Self:
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("Конец курса не может быть раньше начала")
        return self


class MedicationUpdate(PatchSchema):
    name: Name | None = None
    form: Form | None = None
    dose: Name | None = None
    instructions: Instructions | None = None
    start_date: date | None = None
    end_date: date | None = None
    times: list[time] | None = Field(default=None, min_length=1, max_length=12)

    @field_validator("times")
    @classmethod
    def valid_times(cls, values: list[time] | None) -> list[time] | None:
        return validate_times(values) if values is not None else None


class MedicationRead(Schema):
    id: UUID
    member_id: UUID
    name: str
    form: str
    dose: str
    instructions: str
    start_date: date
    end_date: date | None
    times: list[time]


class IntakeCreate(Schema):
    medication_id: UUID
    scheduled_date: date
    scheduled_time: time
    taken: bool = False

    _time = field_validator("scheduled_time")(validate_time)


class IntakeUpdate(PatchSchema):
    scheduled_date: date | None = None
    scheduled_time: time | None = None
    taken: bool | None = None

    @field_validator("scheduled_time")
    @classmethod
    def valid_time(cls, value: time | None) -> time | None:
        return validate_time(value) if value is not None else None


class IntakeRead(Schema):
    id: UUID
    medication_id: UUID
    scheduled_date: date
    scheduled_time: time
    taken: bool
    taken_at: datetime | None


class ScheduleItem(Schema):
    medication_id: UUID
    intake_id: UUID | None
    member_id: UUID
    member_name: str
    medication_name: str
    dose: str
    instructions: str
    scheduled_date: date
    scheduled_time: time
    taken: bool
    taken_at: datetime | None


class DoctorList(Schema):
    day: date
    member: MemberRead
    medications: list[MedicationRead]
    scheduled_count: int
    taken_count: int
