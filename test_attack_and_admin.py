def _create(client, h, key="mykey"):
    return client.post("/api/vault/items", headers=h, json={
        "name": "X", "formula": "Y", "notes": "topsecret", "key": key,
    }).get_json()["item"]["id"]


def test_wrong_key_attack(client, user_token, auth_header):
    h = auth_header(user_token)
    item_id = _create(client, h)
    r = client.post("/api/attack/wrong-key", headers=h,
                    json={"item_id": item_id, "wrong_key": "guess"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["status"] in ("rejected", "decoded_garbage")
    if body["status"] == "decoded_garbage":
        assert body["output"] != "topsecret"


def test_tamper_detected(client, user_token, auth_header):
    h = auth_header(user_token)
    item_id = _create(client, h)
    r = client.post("/api/attack/tamper", headers=h,
                    json={"item_id": item_id, "key": "mykey"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["integrity_ok"] is False
    assert body["verdict"] == "TAMPERING DETECTED"


def test_unauthorized_attack(client):
    r = client.post("/api/attack/unauthorized")
    assert r.status_code == 401


def test_admin_endpoints_require_admin(client, user_token, admin_token, auth_header):
    r = client.get("/api/admin/users", headers=auth_header(user_token))
    assert r.status_code == 403
    r = client.get("/api/admin/users", headers=auth_header(admin_token))
    assert r.status_code == 200


def test_admin_stats(client, admin_token, user_token, auth_header):
    _create(client, auth_header(user_token))
    r = client.get("/api/admin/stats", headers=auth_header(admin_token))
    assert r.status_code == 200
    body = r.get_json()
    assert "totals" in body and body["totals"]["users"] >= 2
    assert "by_event" in body
