import copy

from fastapi.testclient import TestClient

from src import app

client = TestClient(app.app)
INITIAL_ACTIVITIES = copy.deepcopy(app.activities)


def setup_function():
    app.activities.clear()
    app.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_root_redirects_to_static():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_succeeds():
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in app.activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    email = "duplicate_student@mergington.edu"
    first_response = client.post(f"/activities/Programming%20Class/signup?email={email}")
    assert first_response.status_code == 200

    second_response = client.post(f"/activities/Programming%20Class/signup?email={email}")
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_missing_activity_returns_404():
    response = client.post("/activities/Unknown%20Club/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
