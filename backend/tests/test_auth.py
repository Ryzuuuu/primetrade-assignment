from tests.conftest import register_and_login

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"


def test_health_check(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_register_returns_user_without_password(client):
    res = client.post(REGISTER, json={"username": "alice", "email": "alice@example.com", "password": "secret123"})
    assert res.status_code == 201
    body = res.json()
    assert body["username"] == "alice"
    assert body["role"] == "user"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_rejects_duplicate_username_and_email(client):
    payload = {"username": "alice", "email": "alice@example.com", "password": "secret123"}
    assert client.post(REGISTER, json=payload).status_code == 201
    assert client.post(REGISTER, json={**payload, "email": "other@example.com"}).status_code == 400
    assert client.post(REGISTER, json={**payload, "username": "bob"}).status_code == 400


def test_register_validates_input(client):
    base = {"username": "alice", "email": "alice@example.com", "password": "secret123"}
    assert client.post(REGISTER, json={**base, "email": "not-an-email"}).status_code == 422
    assert client.post(REGISTER, json={**base, "password": "123"}).status_code == 422
    assert client.post(REGISTER, json={**base, "username": "ab"}).status_code == 422


def test_login_returns_bearer_token(client):
    client.post(REGISTER, json={"username": "alice", "email": "alice@example.com", "password": "secret123"})
    res = client.post(LOGIN, data={"username": "alice", "password": "secret123"})
    assert res.status_code == 200
    assert res.json()["token_type"] == "bearer"
    assert res.json()["access_token"]


def test_login_rejects_wrong_password_and_unknown_user(client):
    client.post(REGISTER, json={"username": "alice", "email": "alice@example.com", "password": "secret123"})
    assert client.post(LOGIN, data={"username": "alice", "password": "wrong"}).status_code == 401
    assert client.post(LOGIN, data={"username": "nobody", "password": "secret123"}).status_code == 401


def test_protected_route_requires_valid_token(client):
    assert client.get("/api/v1/tasks/").status_code == 401
    res = client.get("/api/v1/tasks/", headers={"Authorization": "Bearer not-a-real-token"})
    assert res.status_code == 401


def test_long_passwords_are_accepted(client):
    password = "p" * 100
    headers = register_and_login(client, "longpass", password=password)
    assert client.get("/api/v1/tasks/", headers=headers).status_code == 200
