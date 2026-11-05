import os

# The app reads its configuration at import time, so set it before importing anything from `app`.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app import models  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

# One shared in-memory SQLite database per test, standing in for PostgreSQL.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def _override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def register_and_login(client, username="alice", email=None, password="secret123", role=None):
    """Create a user (optionally promoting them) and return auth headers for them."""
    email = email or f"{username}@example.com"
    res = client.post("/api/v1/auth/register", json={"username": username, "email": email, "password": password})
    assert res.status_code == 201, res.text
    if role:
        with TestingSession() as db:
            db.query(models.User).filter(models.User.username == username).update({"role": role})
            db.commit()
    res = client.post("/api/v1/auth/login", data={"username": username, "password": password})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture()
def user_headers(client):
    return register_and_login(client, "alice")


@pytest.fixture()
def admin_headers(client):
    return register_and_login(client, "root", role="admin")
