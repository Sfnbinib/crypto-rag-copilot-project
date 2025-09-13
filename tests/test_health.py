import requests

def test_health():
    resp = requests.get("http://127.0.0.1:8000/health", timeout=3)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
