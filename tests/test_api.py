import os
import uuid
import pytest
import requests

base_url = "https://gorest.co.in/public/v2"
TOKEN = os.getenv("GOREST_TOKEN")

pytestmark = pytest.mark.skipif(not TOKEN, reason="Set GOREST_TOKEN first")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def new_user_payload():
    suffix = uuid.uuid4().hex[:8]
    return {
        "name": "Test User",
        "email": f"test.{suffix}@yokohama.com",
        "gender": "male",
        "status": "active",
    }

@pytest.fixture
def created_user():
    resp = requests.post(f"{base_url}/users", json= new_user_payload(), headers=HEADERS)
    assert resp.status_code == 201, resp.text
    user = resp.json()
    yield user
    requests.delete(f"{base_url}/users/{user['id']}", headers=HEADERS)

@pytest.mark.smoke
def test_get_user_returns_list():
    resp = requests.get(f"{base_url}/users", headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) > 0
    for field in ("id", "name", "email", "gender", "status"):
        assert field in body[0]


@pytest.mark.smoke
def test_get_single_user(created_user):
    resp = requests.get(f"{base_url}/users/{created_user['id']}", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["email"] == created_user["email"]


@pytest.mark.smoke
def test_create_user():
    payload = new_user_payload()
    resp = requests.post(f"{base_url}/users", json= payload, headers=HEADERS)
    print("Status:", resp.status_code)
    print("Response:", resp.text)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] > 0
    assert body["name"] == payload["name"]
    assert body["email"] == payload["email"]
    requests.delete(f"{base_url}/users/{body['id']}", headers=HEADERS)


@pytest.mark.regression
def test_create_missing_fields_error():
    resp = requests.post(f"{base_url}/users", json = new_user_payload(), headers= HEADERS)
    assert resp.status_code == 422


@pytest.mark.smoke
def test_update_user(created_user):
    resp = requests.put(f"{base_url}/users/{created_user['id']}",
                        json={"name": "Updated User Put", "status": "inactive"}, headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Updated User Put"
    assert body["status"] == "inactive"

    ## check updated user persist
    check = requests.get(f"{base_url}/users/{created_user['id']}", headers=HEADERS)
    assert check.status_code == 200
    assert check.json()["name"] == 'Updated User Put'


@pytest.mark.smoke
def test_patch_user(created_user):
    original_name = created_user["name"]
    original_email = created_user["email"]
    original_gender = created_user["gender"]

    resp = requests.patch(f"{base_url}/users/{created_user['id']}",
                          json={"status": "inactive"}, headers=HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "inactive"

    ## check that a partial update was made
    assert body["name"] == original_name
    assert body["email"] == original_email
    assert body["gender"] == original_gender


@pytest.mark.smoke
def test_delete_user(created_user):
    resp = requests.delete(f"{base_url}/users/{created_user['id']}", headers=HEADERS)
    assert resp.status_code == 204

    ## check if user still exist
    check = requests.get(f"{base_url}/users/{created_user['id']}", headers=HEADERS)
    assert check.status_code == 404


@pytest.mark.regression
def test_create_user_duplicate_email_fails():
    payload = new_user_payload()
    first = requests.post(f"{base_url}/users", json=payload, headers=HEADERS)
    assert first.status_code == 201, first.text

    duplicate = requests.post(f"{base_url}/users", json=payload, headers=HEADERS)
    assert duplicate.status_code in (409, 422), duplicate.text

    requests.delete(f"{base_url}/users/{first.json()['id']}", headers=HEADERS)


@pytest.mark.regression
def test_create_user_invalid_gender_fails():
    payload = new_user_payload()
    payload["gender"] = "unknown"

    resp = requests.post(f"{base_url}/users", json=payload, headers=HEADERS)
    assert resp.status_code in (400, 422), resp.text


@pytest.mark.regression
def test_create_user_missing_required_fields_fails():
    payload = {"name": "Missing Email User", "gender": "male", "status": "active"}

    resp = requests.post(f"{base_url}/users", json=payload, headers=HEADERS)
    assert resp.status_code in (400, 422), resp.text


@pytest.mark.smoke
def test_get_missing_user_returns_404():
    resp = requests.get(f"{base_url}/users/999999999", headers=HEADERS)
    assert resp.status_code == 404, resp.text


@pytest.mark.regression
def test_update_missing_user_returns_404():
    payload = {"name": "Ghost Update", "status": "inactive"}
    resp = requests.put(f"{base_url}/users/999999999", json=payload, headers=HEADERS)
    assert resp.status_code == 404, resp.text


@pytest.mark.regression
def test_patch_user_keeps_other_fields(created_user):
    original_name = created_user["name"]
    original_email = created_user["email"]
    original_gender = created_user["gender"]

    resp = requests.patch(
        f"{base_url}/users/{created_user['id']}",
        json={"status": "inactive"},
        headers=HEADERS,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "inactive"
    assert body["name"] == original_name
    assert body["email"] == original_email
    assert body["gender"] == original_gender


@pytest.mark.regression
def test_delete_missing_user_returns_404():
    resp = requests.delete(f"{base_url}/users/999999999", headers=HEADERS)
    assert resp.status_code == 404, resp.text


@pytest.mark.smoke
def test_request_without_token_error():
    resp = requests.post(f"{base_url}/users",
                         json=new_user_payload(),
                         headers={"Content-Type": "application/json"}
                         )
    assert resp.status_code == 401
