from datetime import date, time
from uuid import UUID, uuid4

import pytest
from alembic import command
from sqlalchemy import func, inspect, select, text
from sqlalchemy.exc import IntegrityError

from app.models import Family, FamilyMember, Intake, Medication, MedicationTime
from scripts.seed import DEMO_DAY, demo_id, seed_demo


def test_migrations_match_models_and_are_reversible(migrated_database):
    _, engine, config = migrated_database
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.check(config)
        assert set(inspect(connection).get_table_names()) == {
            "alembic_version",
            "families",
            "family_members",
            "medications",
            "medication_times",
            "intakes",
        }
        command.downgrade(config, "base")
        assert inspect(connection).get_table_names() == ["alembic_version"]
        command.upgrade(config, "head")


@pytest.mark.parametrize(
    "violation", ["foreign_key", "unique_slot", "course_dates", "taken_timestamp", "primary_key"]
)
def test_postgresql_constraints(app, records, violation):
    with app.state.database.session_factory() as session:
        if violation == "foreign_key":
            session.add(
                FamilyMember(
                    family_id=uuid4(),
                    full_name="Пример",
                    birth_date=date(2000, 1, 1),
                    relation="Брат",
                )
            )
        elif violation == "unique_slot":
            session.add(
                Intake(
                    medication_id=UUID(records["medications"]["id"]),
                    scheduled_date=date(2020, 1, 2),
                    scheduled_time=time(8),
                    taken=False,
                )
            )
        elif violation == "course_dates":
            med = session.get(Medication, UUID(records["medications"]["id"]))
            med.end_date = date(2019, 12, 31)
        elif violation == "taken_timestamp":
            intake = session.get(Intake, UUID(records["intakes"]["id"]))
            intake.taken = True
            intake.taken_at = None
        else:
            session.add(
                MedicationTime(medication_id=UUID(records["medications"]["id"]), time=time(8))
            )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        assert session.scalar(select(func.count()).select_from(Family)) == 1


def test_seed_idempotence_and_demo_schedule(client, app):
    with app.state.database.session_factory() as session:
        assert seed_demo(session) is True
        assert seed_demo(session) is False
        for model, expected in ((Family, 1), (FamilyMember, 3), (Medication, 5), (Intake, 6)):
            assert session.scalar(select(func.count()).select_from(model)) == expected
        family = session.get(Family, demo_id("family"))
        family.name = "Название после редактирования"
        session.commit()
        assert seed_demo(session) is False
        assert family.name == "Название после редактирования"
    response = client.get(
        "/api/v1/schedule",
        params={"family_id": str(demo_id("family")), "day": DEMO_DAY.isoformat()},
    )
    assert response.status_code == 200
    assert len(response.json()) == 6
    assert sum(slot["taken"] for slot in response.json()) == 2
    with app.state.database.engine.connect() as connection:
        assert connection.scalar(text("SELECT version()")).startswith("PostgreSQL")
