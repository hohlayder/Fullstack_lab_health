from datetime import date, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError

from app.main import create_app
from app.models import Family, FamilyMember, Intake, Medication, MedicationTime

PREFIX = "/api/v1"


@pytest.mark.parametrize(
    ("resource", "changes"),
    [
        ("families", {"name": "Новое название"}),
        ("members", {"full_name": "Анна Иванова", "relation": "Сестра"}),
        ("medications", {"dose": "2 таблетки", "instructions": "Утром"}),
        ("intakes", {"taken": True}),
    ],
)
def test_crud_and_persistence(client, app, records, resource, changes):
    record = records[resource]
    path = f"{PREFIX}/{resource}/{record['id']}"
    assert client.get(path).json() == record
    assert record in client.get(f"{PREFIX}/{resource}").json()
    response = client.patch(path, json=changes)
    assert response.status_code == 200
    for field, value in changes.items():
        assert response.json()[field] == value
    model = {
        "families": Family,
        "members": FamilyMember,
        "medications": Medication,
        "intakes": Intake,
    }[resource]
    with app.state.database.session_factory() as session:
        stored = session.get(model, UUID(record["id"]))
        assert stored is not None
        for field, value in changes.items():
            assert getattr(stored, field) == value
    # A new application, pool and session must read the committed data.
    restarted = create_app(app_settings(app))
    with TestClient(restarted) as second_client:
        assert second_client.get(path).json() == response.json()
    deleted = client.delete(path)
    assert deleted.status_code == 204 and deleted.content == b""
    assert client.get(path).status_code == 404
    assert client.patch(path, json=changes).status_code == 404
    assert client.delete(path).status_code == 404


def app_settings(app):
    from pydantic import SecretStr

    from app.core.config import Settings

    return Settings(
        _env_file=None,
        database_url=SecretStr(app.state.database.engine.url.render_as_string(hide_password=False)),
    )


@pytest.mark.parametrize("resource", ["families", "members", "medications", "intakes"])
def test_missing_invalid_ids_and_patch(client, records, resource):
    assert client.get(f"{PREFIX}/{resource}/{uuid4()}").status_code == 404
    assert client.get(f"{PREFIX}/{resource}/bad-uuid").status_code == 422
    path = f"{PREFIX}/{resource}/{records[resource]['id']}"
    assert client.patch(path, json={}).status_code == 422
    assert client.patch(path, json={"unknown": "value"}).status_code == 422
    field = {"families": "name", "members": "relation", "medications": "dose", "intakes": "taken"}[
        resource
    ]
    assert client.patch(path, json={field: None}).status_code == 422
    assert client.get(path).json() == records[resource]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", "   "),
        ("name", "a" * 121),
        ("times", []),
        ("times", ["08:00", "08:00"]),
        ("times", ["08:00:01"]),
        ("times", ["08:00+03:00"]),
        ("times", ["25:00"]),
        ("end_date", "2019-12-31"),
        ("start_date", "bad-date"),
        ("instructions", "a" * 2001),
        ("unknown", "value"),
    ],
)
def test_medication_validation(client, records, field, value):
    body = {
        key: records["medications"][key]
        for key in (
            "member_id",
            "name",
            "form",
            "dose",
            "instructions",
            "start_date",
            "end_date",
            "times",
        )
    }
    body[field] = value
    response = client.post(f"{PREFIX}/medications", json=body)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert len(client.get(f"{PREFIX}/medications").json()) == 1


def test_foreign_keys_and_member_validation(client, records):
    body = {
        "family_id": str(uuid4()),
        "full_name": "Иван",
        "birth_date": "2000-01-01",
        "relation": "Брат",
    }
    assert client.post(f"{PREFIX}/members", json=body).status_code == 404
    body["family_id"] = records["families"]["id"]
    for birthday in ((date.today() + timedelta(days=1)).isoformat(), "1899-12-31"):
        body["birth_date"] = birthday
        assert client.post(f"{PREFIX}/members", json=body).status_code == 422
    prescription = {
        "member_id": str(uuid4()),
        "name": "Пример",
        "form": "Таблетки",
        "dose": "1",
        "start_date": "2020-01-01",
        "times": ["08:00"],
    }
    assert client.post(f"{PREFIX}/medications", json=prescription).status_code == 404
    assert (
        client.post(
            f"{PREFIX}/intakes",
            json={
                "medication_id": str(uuid4()),
                "scheduled_date": "2020-01-02",
                "scheduled_time": "08:00",
            },
        ).status_code
        == 404
    )


def test_intake_toggle_conflict_and_rollback(client, records):
    record = records["intakes"]
    path = f"{PREFIX}/intakes/{record['id']}"
    taken = client.patch(path, json={"taken": True}).json()
    assert taken["taken"] and datetime.fromisoformat(taken["taken_at"]).utcoffset() is not None
    assert client.patch(path, json={"taken": True}).json()["taken_at"] == taken["taken_at"]
    assert client.patch(path, json={"taken": False}).json()["taken_at"] is None
    body = {
        key: record[key] for key in ("medication_id", "scheduled_date", "scheduled_time", "taken")
    }
    duplicate = client.post(f"{PREFIX}/intakes", json=body)
    assert duplicate.status_code == 409 and "уже существует" in duplicate.json()["detail"]
    # An integrity failure must not poison the next request's session.
    body["scheduled_time"] = "20:00"
    assert client.post(f"{PREFIX}/intakes", json=body).status_code == 201
    assert client.patch(path, json={"scheduled_time": "20:00"}).status_code == 409
    assert client.get(path).json()["scheduled_time"] == "08:00:00"
    assert client.patch(path, json={"taken": True}).status_code == 200


def test_intake_course_time_and_future_validation(client, records):
    body = {
        "medication_id": records["medications"]["id"],
        "scheduled_date": "2020-01-02",
        "scheduled_time": "12:00",
    }
    assert client.post(f"{PREFIX}/intakes", json=body).status_code == 422
    body.update(scheduled_time="08:00", scheduled_date="2019-12-31")
    assert client.post(f"{PREFIX}/intakes", json=body).status_code == 422
    body.update(scheduled_date=(date.today() + timedelta(days=1)).isoformat(), taken=True)
    assert client.post(f"{PREFIX}/intakes", json=body).status_code == 422
    body["taken"] = False
    response = client.post(f"{PREFIX}/intakes", json=body)
    assert response.status_code == 201
    assert (
        client.patch(f"{PREFIX}/intakes/{response.json()['id']}", json={"taken": True}).status_code
        == 422
    )


def test_medication_updates_keep_history(client, records):
    path = f"{PREFIX}/medications/{records['medications']['id']}"
    assert client.patch(path, json={"times": ["08:00", "21:00"]}).json()["times"] == [
        "08:00:00",
        "21:00:00",
    ]
    assert client.patch(path, json={"times": ["21:00"]}).status_code == 409
    assert client.patch(path, json={"start_date": "2020-01-03"}).status_code == 409
    assert client.patch(path, json={"end_date": "2019-12-31"}).status_code == 422
    assert client.patch(path, json={"end_date": "2020-01-02"}).status_code == 200
    assert client.patch(path, json={"end_date": "2020-01-01"}).status_code == 409
    assert client.patch(path, json={"end_date": None}).json()["end_date"] is None
    assert client.get(path).json()["start_date"] == "2020-01-01"


@pytest.mark.parametrize("resource", ["families", "members", "medications"])
def test_cascade_deletion(client, app, records, resource):
    assert client.delete(f"{PREFIX}/{resource}/{records[resource]['id']}").status_code == 204
    with app.state.database.session_factory() as session:
        for model in (Medication, MedicationTime, Intake):
            assert session.scalar(select(func.count()).select_from(model)) == 0
        if resource in ("families", "members"):
            assert session.scalar(select(func.count()).select_from(FamilyMember)) == 0
        expected = 0 if resource == "families" else 1
        assert session.scalar(select(func.count()).select_from(Family)) == expected


def test_schedule_filters_and_doctor_list(client, records):
    family, member, med = (records[key] for key in ("families", "members", "medications"))
    params = {"family_id": family["id"], "day": "2020-01-02"}
    schedule = client.get(f"{PREFIX}/schedule", params=params).json()
    assert len(schedule) == 2
    assert [slot["scheduled_time"] for slot in schedule] == ["08:00:00", "20:00:00"]
    assert schedule[1]["intake_id"] is None and not schedule[1]["taken"]
    client.patch(f"{PREFIX}/intakes/{records['intakes']['id']}", json={"taken": True})
    assert len(client.get(f"{PREFIX}/schedule", params={**params, "taken": True}).json()) == 1
    assert len(client.get(f"{PREFIX}/schedule", params={**params, "taken": False}).json()) == 1
    assert client.get(f"{PREFIX}/schedule", params={**params, "day": "2019-12-31"}).json() == []
    # Another day has its own marks; reading a schedule never inserts records.
    tomorrow = client.get(f"{PREFIX}/schedule", params={**params, "day": "2020-01-03"}).json()
    assert all(slot["intake_id"] is None and not slot["taken"] for slot in tomorrow)
    assert len(client.get(f"{PREFIX}/intakes").json()) == 1
    report = client.get(
        f"{PREFIX}/members/{member['id']}/doctor-list", params={"day": "2020-01-02"}
    ).json()
    assert report["member"]["id"] == member["id"]
    assert report["medications"][0]["id"] == med["id"]
    assert (report["scheduled_count"], report["taken_count"]) == (2, 1)
    other = client.post(f"{PREFIX}/families", json={"name": "Другая семья"}).json()
    assert (
        client.get(f"{PREFIX}/schedule", params={**params, "family_id": other["id"]}).json() == []
    )
    for endpoint in ("schedule", "medications", "intakes"):
        response = client.get(
            f"{PREFIX}/{endpoint}",
            params={**params, "family_id": other["id"], "member_id": member["id"]},
        )
        assert response.status_code == 422
    assert (
        client.get(
            f"{PREFIX}/intakes", params={"family_id": other["id"], "medication_id": med["id"]}
        ).status_code
        == 422
    )
    for endpoint in ("members", "medications", "intakes", "schedule"):
        assert (
            client.get(
                f"{PREFIX}/{endpoint}", params={**params, "family_id": str(uuid4())}
            ).status_code
            == 404
        )


def test_pagination_health_openapi_and_cors(client, records):
    for name in ("Б", "В"):
        client.post(f"{PREFIX}/families", json={"name": name})
    all_families = client.get(f"{PREFIX}/families").json()
    assert (
        client.get(f"{PREFIX}/families", params={"offset": 1, "limit": 1}).json()
        == all_families[1:2]
    )
    for params in ({"offset": -1}, {"limit": 0}, {"limit": 201}):
        assert client.get(f"{PREFIX}/families", params=params).status_code == 422
    assert client.get("/health").json() == {"status": "ok", "database": "postgresql"}
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/docs").status_code == 200
    response = client.options(
        f"{PREFIX}/families",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_database_error_does_not_expose_connection(client, app, monkeypatch):
    def unavailable(*args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("secret password and database URL"))

    monkeypatch.setattr(app.state.database.engine, "connect", unavailable)
    response = client.get("/health")
    assert response.status_code == 503
    assert "secret" not in response.text and "password" not in response.text
