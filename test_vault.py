def _create(client, headers, key="mykey", notes="secret notes"):
    return client.post("/api/vault/items", headers=headers, json={
        "name": "Caffeine", "formula": "C8H10N4O2", "notes": notes, "key": key,
    })


def test_create_list_decrypt_delete(client, user_token, auth_header):
    h = auth_header(user_token)
    r = _create(client, h)
    assert r.status_code == 200
    item_id = r.get_json()["item"]["id"]

    r = client.get("/api/vault/items", headers=h)
    assert r.status_code == 200
    items = r.get_json()["items"]
    assert len(items) == 1
    assert set(items[0]["encrypted_notes"]) <= set("ATGC")

    r = client.post(f"/api/vault/items/{item_id}/decrypt",
                    headers=h, json={"key": "mykey"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["notes"] == "secret notes"
    assert body["integrity_ok"] is True

    r = client.post(f"/api/vault/items/{item_id}/decrypt",
                    headers=h, json={"key": "wrong"})
    assert r.status_code == 400

    r = client.delete(f"/api/vault/items/{item_id}", headers=h)
    assert r.status_code == 200


def test_user_cannot_access_other_users_item(client, user_token, auth_header):
    # alice creates an item
    h_alice = auth_header(user_token)
    item_id = _create(client, h_alice).get_json()["item"]["id"]

    # mallory registers + logs in
    client.post("/api/auth/register", json={"username": "mallory", "password": "password123"})
    tok = client.post("/api/auth/login", json={
        "username": "mallory", "password": "password123",
    }).get_json()["token"]
    h_m = auth_header(tok)

    r = client.post(f"/api/vault/items/{item_id}/decrypt",
                    headers=h_m, json={"key": "mykey"})
    assert r.status_code == 403


def test_admin_sees_all_items(client, user_token, admin_token, auth_header):
    _create(client, auth_header(user_token))
    r = client.get("/api/vault/items", headers=auth_header(admin_token))
    assert r.status_code == 200
    assert len(r.get_json()["items"]) >= 1


def test_visualize(client, user_token, auth_header):
    r = client.post("/api/vault/visualize", headers=auth_header(user_token),
                    json={"text": "abc", "key": "k"})
    assert r.status_code == 200
    body = r.get_json()
    assert set(body["mutated"]) <= set("ATGC")
    assert "complement" in body
