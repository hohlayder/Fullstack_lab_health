from datetime import date, datetime, time, timezone
from uuid import NAMESPACE_URL, UUID, uuid5
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.session import Database
from app.models import Family, FamilyMember, Intake, Medication, MedicationTime

DEMO_DAY = date(2026, 10, 7)


def demo_id(label: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"blizkie/demo/{label}")


def seed_demo(session: Session) -> bool:
    family_id = demo_id("family")
    if session.get(Family, family_id) is not None:
        return False
    family = Family(id=family_id, name="Семья Соколовых")
    people = [
        ("anna", "Анна Соколова", date(2002, 5, 14), "Я"),
        ("elena", "Елена Соколова", date(1967, 3, 20), "Мама"),
        ("mikhail", "Михаил Соколов", date(1964, 6, 12), "Папа"),
    ]
    members = {}
    for key, name, birth_date, relation in people:
        member = FamilyMember(
            id=demo_id(key), full_name=name, birth_date=birth_date, relation=relation
        )
        family.members.append(member)
        members[key] = member
    prescriptions = [
        ("vitamin-d", "anna", "Витамин D", "Капсулы", "1 капсула", ["08:00"], 31, "После завтрака"),
        (
            "medicine-a",
            "elena",
            "Препарат А",
            "Таблетки",
            "1 таблетка",
            ["08:30", "20:00"],
            31,
            "После еды",
        ),
        ("magnesium", "anna", "Магний", "Таблетки", "1 таблетка", ["13:00"], 21, "Во время обеда"),
        (
            "medicine-b",
            "mikhail",
            "Препарат Б",
            "Таблетки",
            "1 таблетка",
            ["14:00"],
            14,
            "После обеда",
        ),
        ("omega", "mikhail", "Омега-3", "Капсулы", "1 капсула", ["19:00"], 31, "Во время ужина"),
    ]
    for key, person, name, form, dose, times, end_day, instructions in prescriptions:
        medication = Medication(
            id=demo_id(key),
            name=name,
            form=form,
            dose=dose,
            instructions=instructions,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, end_day),
        )
        members[person].medications.append(medication)
        for value in times:
            scheduled_time = time.fromisoformat(value)
            medication.dose_times.append(MedicationTime(time=scheduled_time))
            taken = scheduled_time < time(12)
            medication.intakes.append(
                Intake(
                    id=demo_id(f"{key}/{value}"),
                    scheduled_date=DEMO_DAY,
                    scheduled_time=scheduled_time,
                    taken=taken,
                    taken_at=datetime.combine(
                        DEMO_DAY, scheduled_time, ZoneInfo("Europe/Moscow")
                    ).astimezone(timezone.utc)
                    if taken
                    else None,
                )
            )
    session.add(family)
    session.commit()
    return True


def main():
    database = Database(Settings().database_url.get_secret_value())
    try:
        with database.session_factory() as session:
            created = seed_demo(session)
        print(
            "Demo data created."
            if created
            else "Demo family already exists; existing records preserved."
        )
        print(f"Demo family ID: {demo_id('family')}")
    finally:
        database.engine.dispose()


if __name__ == "__main__":
    main()
