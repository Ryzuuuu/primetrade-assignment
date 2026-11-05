from tests.conftest import register_and_login

TASKS = "/api/v1/tasks/"


def create_task(client, headers, title="Write tests", description=None):
    res = client.post(TASKS, json={"title": title, "description": description}, headers=headers)
    assert res.status_code == 201, res.text
    return res.json()


def test_create_and_list_own_tasks(client, user_headers):
    task = create_task(client, user_headers, "Buy milk", "2 litres")
    assert task["title"] == "Buy milk"
    assert task["completed"] is False

    res = client.get(TASKS, headers=user_headers)
    assert res.status_code == 200
    assert [t["id"] for t in res.json()] == [task["id"]]


def test_create_task_validates_title(client, user_headers):
    assert client.post(TASKS, json={"title": ""}, headers=user_headers).status_code == 422
    assert client.post(TASKS, json={}, headers=user_headers).status_code == 422


def test_users_only_see_their_own_tasks(client, user_headers):
    create_task(client, user_headers, "alice task")
    bob = register_and_login(client, "bob")
    create_task(client, bob, "bob task")

    titles = [t["title"] for t in client.get(TASKS, headers=bob).json()]
    assert titles == ["bob task"]


def test_admin_sees_all_tasks(client, user_headers, admin_headers):
    create_task(client, user_headers, "alice task")
    create_task(client, admin_headers, "admin task")

    assert len(client.get(TASKS, headers=admin_headers).json()) == 2
    assert len(client.get(f"{TASKS}admin/all", headers=admin_headers).json()) == 2


def test_admin_endpoint_is_forbidden_for_regular_users(client, user_headers):
    assert client.get(f"{TASKS}admin/all", headers=user_headers).status_code == 403


def test_update_task_partial(client, user_headers):
    task = create_task(client, user_headers, "Draft", "keep me")
    res = client.put(f"{TASKS}{task['id']}", json={"completed": True}, headers=user_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["completed"] is True
    assert body["title"] == "Draft"
    assert body["description"] == "keep me"


def test_user_cannot_modify_someone_elses_task(client, user_headers):
    task = create_task(client, user_headers)
    bob = register_and_login(client, "bob")

    assert client.put(f"{TASKS}{task['id']}", json={"title": "hacked"}, headers=bob).status_code == 403
    assert client.delete(f"{TASKS}{task['id']}", headers=bob).status_code == 403


def test_admin_can_modify_and_delete_any_task(client, user_headers, admin_headers):
    task = create_task(client, user_headers)

    res = client.put(f"{TASKS}{task['id']}", json={"completed": True}, headers=admin_headers)
    assert res.status_code == 200
    assert client.delete(f"{TASKS}{task['id']}", headers=admin_headers).status_code == 204
    assert client.get(TASKS, headers=user_headers).json() == []


def test_missing_task_returns_404(client, user_headers):
    assert client.put(f"{TASKS}999", json={"title": "x"}, headers=user_headers).status_code == 404
    assert client.delete(f"{TASKS}999", headers=user_headers).status_code == 404


def test_delete_removes_task(client, user_headers):
    task = create_task(client, user_headers)
    assert client.delete(f"{TASKS}{task['id']}", headers=user_headers).status_code == 204
    assert client.get(TASKS, headers=user_headers).json() == []
