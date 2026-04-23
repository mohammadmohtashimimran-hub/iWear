"""Health and public endpoints (no auth)."""
def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("status") == "ok"


def test_settings_get(client):
    r = client.get("/api/settings/")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, dict)
