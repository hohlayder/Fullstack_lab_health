import os
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings
from app.main import create_app

BACKEND = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def postgres_url():
    value = os.environ.get("TEST_DATABASE_URL") or dotenv_values(BACKEND / ".env").get(
        "TEST_DATABASE_URL"
    )
    if not value:
        raise pytest.UsageError("Set TEST_DATABASE_URL to a PostgreSQL database ending in _test.")
    try:
        url = make_url(value)
    except Exception:
        raise pytest.UsageError("TEST_DATABASE_URL is invalid.") from None
    if url.drivername != "postgresql+psycopg" or not (url.database or "").endswith("_test"):
        raise pytest.UsageError("Tests require postgresql+psycopg and a database ending in _test.")
    return url


@pytest.fixture
def migrated_database(postgres_url):
    # Each test owns one schema; application data and other schemas remain intact.
    schema = f"lab2_test_{uuid4().hex}"
    admin = create_engine(postgres_url, connect_args={"connect_timeout": 5})
    try:
        with admin.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    except SQLAlchemyError:
        admin.dispose()
        raise pytest.UsageError(
            "Cannot create a test schema. Start PostgreSQL and check TEST_DATABASE_URL."
        ) from None
    url = postgres_url.update_query_dict({"options": f"-csearch_path={schema}"})
    engine = create_engine(url)
    config = Config(str(BACKEND / "alembic.ini"))
    try:
        with engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")
        yield url, engine, config
    finally:
        engine.dispose()
        with admin.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


@pytest.fixture
def app(migrated_database):
    url, _, _ = migrated_database
    settings = Settings(
        _env_file=None, database_url=SecretStr(url.render_as_string(hide_password=False))
    )
    application = create_app(settings)
    yield application
    application.state.database.engine.dispose()


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def records(client):
    def create(path, body):
        response = client.post(f"/api/v1/{path}", json=body)
        assert response.status_code == 201, response.text
        assert response.headers["location"] == f"/api/v1/{path}/{response.json()['id']}"
        return response.json()

    family = create("families", {"name": "Семья Петровых"})
    member = create(
        "members",
        {
            "family_id": family["id"],
            "full_name": "Анна Петрова",
            "birth_date": "2000-05-14",
            "relation": "Дочь",
        },
    )
    medication = create(
        "medications",
        {
            "member_id": member["id"],
            "name": "Учебный препарат",
            "form": "Таблетки",
            "dose": "1 таблетка",
            "instructions": "После еды",
            "start_date": "2020-01-01",
            "end_date": None,
            "times": ["20:00", "08:00"],
        },
    )
    intake = create(
        "intakes",
        {
            "medication_id": medication["id"],
            "scheduled_date": "2020-01-02",
            "scheduled_time": "08:00",
            "taken": False,
        },
    )
    return {"families": family, "members": member, "medications": medication, "intakes": intake}
