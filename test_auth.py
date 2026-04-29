def test_register_then_login(client):
    r = client.post("/api/auth/register", json={
        "username": "bob", "password": "secret123", "role": "user",
    })
    assert r.status_code == 200
    body = r.get_json()
    assert body["user"]["username"] == "bob"
    assert body["token"]

    r = client.post("/api/auth/login", json={
        "username": "bob", "password": "secret123",
    })
    assert r.status_code == 200


def test_short_password_rejected(client):
    r = client.post("/api/auth/register", json={
        "username": "bob", "password": "x",
    })
    assert r.status_code == 400


def test_duplicate_username(client):
    client.post("/api/auth/register", json={"username": "bob", "password": "secret123"})
    r = client.post("/api/auth/register", json={"username": "bob", "password": "secret123"})
    assert r.status_code == 409


def test_brute_force_lockout(client):
    client.post("/api/auth/register", json={"username": "bob", "password": "secret123"})
    # 3 wrong attempts (LOGIN_MAX_ATTEMPTS=3 in test config)
    for _ in range(3):
        client.post("/api/auth/login", json={"username": "bob", "password": "wrong"})
    r = client.post("/api/auth/login", json={"username": "bob", "password": "secret123"})
    assert r.status_code == 429
    assert "retry_after" in r.get_json()


def test_protected_route_requires_token(client):
    r = client.get("/api/vault/items")
    assert r.status_code == 401
