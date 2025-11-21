import uuid

from fastapi.testclient import TestClient


def test_create_user_success(client: TestClient, user_payload: dict):
    response = client.post("/api/v1/users/", json=user_payload)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["login"] == user_payload["login"]
    assert data["project_id"] == user_payload["project_id"]
    assert data["env"] == user_payload["env"]
    assert data["domain"] == user_payload["domain"]
    assert data["locktime"] is None


def test_create_user_duplicate_login(client: TestClient, user_payload: dict):
    # первый раз создаём
    response_1 = client.post("/api/v1/users/", json=user_payload)
    assert response_1.status_code == 201

    # второй раз с тем же логином
    response_2 = client.post("/api/v1/users/", json=user_payload)
    assert response_2.status_code == 400
    data = response_2.json()
    assert data["detail"] == "User with this login already exists."


def test_get_users_returns_list(client: TestClient, user_payload: dict):
    # создаём одного пользователя
    client.post("/api/v1/users/", json=user_payload)

    response = client.get("/api/v1/users/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    user = data[0]
    assert "id" in user
    assert "login" in user
    assert "project_id" in user


def test_acquire_lock_success(client: TestClient, user_payload: dict):
    # сначала создаём пользователя
    create_resp = client.post("/api/v1/users/", json=user_payload)
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    # накладываем блокировку
    lock_resp = client.post(f"/api/v1/users/{user_id}/acquire")
    assert lock_resp.status_code == 200

    data = lock_resp.json()
    assert data["id"] == user_id
    assert data["locked"] is True
    assert data["locktime"] is not None
    assert data["message"] == "User successfully locked."


def test_acquire_lock_already_locked(client: TestClient, user_payload: dict):
    # создаём пользователя
    create_resp = client.post("/api/v1/users/", json=user_payload)
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    # первый раз — успешно
    first_lock = client.post(f"/api/v1/users/{user_id}/acquire")
    assert first_lock.status_code == 200

    # второй раз — конфликт
    second_lock = client.post(f"/api/v1/users/{user_id}/acquire")
    assert second_lock.status_code == 409
    data = second_lock.json()
    assert data["detail"] == "User is already locked."


def test_release_lock_success(client: TestClient, user_payload: dict):
    # создаём пользователя
    create_resp = client.post("/api/v1/users/", json=user_payload)
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    # лочим
    lock_resp = client.post(f"/api/v1/users/{user_id}/acquire")
    assert lock_resp.status_code == 200

    # снимаем блокировку
    unlock_resp = client.post(f"/api/v1/users/{user_id}/release")
    assert unlock_resp.status_code == 200

    data = unlock_resp.json()
    assert data["id"] == user_id
    assert data["locked"] is False
    assert data["locktime"] is None
    assert data["message"] == "User successfully unlocked."


def test_release_lock_when_not_locked(client: TestClient, user_payload: dict):
    # создаём пользователя
    create_resp = client.post("/api/v1/users/", json=user_payload)
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    # сразу пробуем снять блокировку, не лоча
    unlock_resp = client.post(f"/api/v1/users/{user_id}/release")
    assert unlock_resp.status_code == 200

    data = unlock_resp.json()
    assert data["id"] == user_id
    assert data["locked"] is False
    assert data["locktime"] is None
    assert data["message"] == "User was not locked."


def test_acquire_lock_user_not_found(client: TestClient):
    random_id = str(uuid.uuid4())
    resp = client.post(f"/api/v1/users/{random_id}/acquire")
    assert resp.status_code == 404
    data = resp.json()
    assert data["detail"] == "User not found."


def test_release_lock_user_not_found(client: TestClient):
    random_id = str(uuid.uuid4())
    resp = client.post(f"/api/v1/users/{random_id}/release")
    assert resp.status_code == 404
    data = resp.json()
    assert data["detail"] == "User not found."
