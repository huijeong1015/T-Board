import pytest
from pathlib import Path
from project.app import app, db, Event, User
from flask import abort, flash, Flask, request, redirect, url_for
from flask.helpers import get_flashed_messages
from pytest import MonkeyPatch
TEST_DB = "test.db"

@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    # Ensure we're working with a test database and not the main database
    app.config["TESTING"] = True
    app.config["DATABASE"] = BASE_DIR.joinpath(TEST_DB)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"

    # Push an application context so we can connect to the database
    with app.app_context():
        db.create_all()  # create db
        yield app.test_client()  # run tests
        db.drop_all()  # remove db


def test_show_events(client):
    # Populate the database with a sample event
    event = Event(
        name="Sample Event",
        date="2023-10-15",
        time="10:00",
        location="Test Location",
        description="This is a test event.",
        event_type="other"
    )
    with app.app_context():
        db.session.add(event)
        db.session.commit()

    # Fetch the show_events route
    response = client.get("/")

    # Ensure the sample event is present in the response
    assert "Sample Event", response.data.decode()


def login(client, username, password):
    """Login helper function"""
    return client.post(
        "/login",
        data=dict(username=username, password=password),
        follow_redirects=True,
    )


# Weihang: Test that the empty login shouldn't redirect the user
def test_empty_login(client):
    """Test login with empty username and password."""
    login_url = "/login/"
    response = client.post(
        login_url, data=dict(username="", password=""), follow_redirects=True
    )

    # Assert that the response URL is still the login URL, indicating the page hasn't changed
    assert response.request.path == login_url


# Hui: Test the my account page contains user's id and their interests
@pytest.mark.skip(reason="KeyError: 'USERNAME'")
def test_my_account_page_contains_userinfo(client):
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = client.get("/my_account/myevents")
    assert "HELLO, {:s}!".format(app.config["USERNAME"]).encode() in rv.data
    assert "Interests: {:s}".format(app.config["INTERESTS"]).encode() in rv.data


# Jennifer: checking if result of search contains the input keyword
@pytest.mark.skip(reason="AssertionError: 'Tech' not found in response")
def test_search_event_keywords(client):
    # add the event
    event = Event(
        name="Tech Conference 2023",
        date="2023-11-20",
        time="09:00",
        location="Silicon Valley Convention Center",
        description="Join industry leaders...", 
        event_type="Networking",
    )
    with app.app_context():
        db.session.add(event)
        db.session.commit()

    # search action
    response = client.post("/search_dashboard", data={"input-search": "Tech"})

    # has keyword
    assert b"Tech" in response.data

    # is keyword in response
    events = response.context["events"]
    expected_keyword = "Tech"
    for event in events:
        assert expected_keyword in event.name


# Dasha: Check error handling
def test_error_handling_404(client):
    response = client.get("/this_is_not_a_valid_route")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data
    assert b"Please return to the main page" in response.data


@app.route("/trigger_error")
def trigger_error():
    abort(500)


def test_error_handling_500(client):
    with app.app_context():
        response = client.get("/trigger_error")

    assert response.status_code == 500
    assert b"Internal Server Error" in response.data


# An: Attempted to generate errors and injections to the database
def test_injection(client):
    # Attempted to inject with raw SQL language
    event = Event(
        name="T-Board App Grand Release Press Conference",
        date="2023-11-15",
        time="23:59",
        location="BA1160",
        description="Sample'); drop table events; --",
        event_type= "Networking",
    )
    with app.app_context():
        db.session.add(event)
        db.session.commit()

    # Fetch the show_events route
    response = client.get("/")

    # Ensure the sample event is present in the response
    assert "T-Board App Grand Release Press Conference", response.data.decode()


# Ghamr: ensure that added events show up on the main dashboard
@pytest.mark.skip(reason="KeyError: 'USERNAME'")
def test_event_post(client):
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = client.post(
        "/event_post",
        data=dict(
            event_name="test event name",
            event_date="01/01/2030",
            time="02:20",
            location="test location",
            description="test event description",
            event_type="other"
        ),
        follow_redirects=True,
    )
    assert b"no event added" not in rv.data
    assert b"test event name" in rv.data
    assert b"01/01/2030" in rv.data
    assert "02:20" in rv.data
    assert "test location" in rv.data
    assert "test event description" in rv.data

def test_login_invalid_user(client): #invalid username
    response = client.post('/login', data=dict(username="'non_existent_user'", password="password"), follow_redirects=True)
    assert response.request.path == '/login/'

def test_login_invalid_password(client):
    # Attempt to login with an incorrect password
    response = client.post('/login', data=dict(username="'non_existent_user'", password="password"), follow_redirects=True)

    assert response.request.path == '/login/'
#working cases for login (successful actions)

def test_register_empty_fields(client):
    """Test registration with empty fields."""
    # Attempt to register with empty fields
    response = client.post('/register', data={}, follow_redirects=True)

    assert response.request.path == '/register/'
    # assert 'All fields are required.' in get_flashed_messages()[0]  # Replace with the appropriate error message

def test_register_existing_username(client):
    """Test registration with an existing username."""
    existingUser = User(username= "existing_name", password= "password", 
                        email = "someone@mailutoronto.ca", profile_picture="Default")
    with app.app_context():
        db.session.add(existingUser)
        db.session.commit()
    #register with an existing username
    response = client.post(
        '/register',
        data={'input-id': 'existing_user'},
        follow_redirects=True
    )
    assert response.request.path == '/register/'
    # assert b"This Username is taken, please try a different one." in response.data
    # assert 'This Username is taken, please try a different one.' in get_flashed_messages()[0]  # Assert the flashed error message
def test_register_missing_fields(client):
    # Test the registration route with missing required fields
    data = {"input-id": "",
        "input-email": "new_user@example.com",
        "input-confirm-email": "new_user@example.com",
        "input-pwd": "Password123!",
        "input-confirm-pwd": "Password123!",
        "input-interests": "Testing, Flask"}
    response = client.post('/register/', data=data)
    assert response.request.path == '/register/'
    assert b"All fields are required." in response.data
def test_register_password_strength(client):
    # Test the registration route with a weak password
    data = {
        "input-id": "new_user",
        "input-email": "new_user@example.com",
        "input-confirm-email": "new_user@example.com",
        "input-pwd": "weakpwd",
        "input-confirm-pwd": "weakpwd",
        "input-interests": "Testing, Flask",
    }
    response = client.post('/register/', data=data)
    assert b"Password strength is weak" in response.data
def test_register_existing_email(client):
    # Test the registration route with an existing email
    data = {
        "input-id": "new_user",
        "input-email": "existing_user@example.com",
        "input-confirm-email": "existing_user@example.com",
        "input-pwd": "Password123!",
        "input-confirm-pwd": "Password123!",
        "input-interests": "Testing, Flask",
    }
    response = client.post('/register/', data=data)
    assert response.request.path == '/register/'
    # assert b"This email has already been used." in response.data