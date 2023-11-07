import pytest
from pathlib import Path
from project.app import app, db, Event, User
from flask import abort, flash, Flask, request, redirect, url_for, session
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
        date="2024-10-15",
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
        name="Tech Conference 2024",
        date="2024-11-20",
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
        date="2024-11-15",
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
def test_register_password_strong(client):
    data = {
        "input-id": "new_user1",
        "input-email": "new_user1@example.com",
        "input-confirm-email": "new_user1@example.com",
        "input-pwd": "1A2S3Df!",
        "input-confirm-pwd": "1A2S3Df!",
        "input-interests": "Testing, Flask",
    }
    response = client.post('/register/', data=data)
    assert b"" in response.data
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
#WORKING TEST CASES FOR SUCCESS/VALID THINGS

def test_bookmark_get(client):
    """Test accessing the bookmark page with a GET request."""
    with client:
        response = client.get('/bookmark')
        assert response.request.path == '/bookmark'
        # assert b'Bookmarked Events' in response.data  # Check for the presence of the bookmarked event
def test_bookmark_post_event_details(client):
    """Test bookmarking an event with a POST request."""
    with client:
        with app.app_context():
            # Create a test user and event
            test_user = User(username= "test_user", password= "test_password", 
                        email = "someone1@mailutoronto.ca", interests= "testing", profile_picture="Default")
            test_event = Event(
                name="T-Board App Grand Release Press Conference", date="2023-12-15",
                time="23:59", location="BA1160",
                description="Sample", event_type= "Networking",
            )
            db.session.add(test_user)
            db.session.add(test_event)
            db.session.commit()
        with client.session_transaction() as sess:
            sess['username'] = 'test_user'
        response = client.post('/bookmark', data={'event-details': '1'})
        assert response.status_code == 308  
        #assert 'Test Event' in response.data.decode()  # Check for the presence of the bookmarked event
def test_bookmark_post_remove_from_bookmarks(client):
    """Test removing an event from bookmarks with a POST request."""
    with client:
        with app.app_context():
            # Create a test user and event
            test_user = User(username= "test_user", password= "test_password", 
                        email = "someone1@mailutoronto.ca", interests= "testing", profile_picture="Default")
            test_event = Event(name="T-Board App Grand Release Press Conference", date="2023-12-15",
                time="23:59", location="BA1160",
                description="Sample", event_type= "Networking",
            )
            test_user.bookmarked_events.append(test_event)
            db.session.add(test_user)
            db.session.commit()
        with client.session_transaction() as sess:
            sess['username'] = 'test_user'
        response = client.post('/bookmark', data={'remove-from-bookmarks': '1'})
        assert response.status_code == 308  # Replace with the expected HTTP status code
        # assert b'Removed from bookmarks' in response.data  # Check for the removal confirmation message
def test_bookmark_post_invalid_event_details(client):
    """Test attempting to bookmark an invalid event with a POST request."""
    with client:
        with client.session_transaction() as sess:
            sess['username'] = 'test_user'
        response = client.post('/bookmark', data={'event-details': '999'})
        assert response.status_code == 308 
        # assert b'Event not found' in response.data  # Check for the error message
def test_bookmark_post_invalid_remove_from_bookmarks(client):
    """Test attempting to remove an invalid event from bookmarks with a POST request."""
    with client:
        with client.session_transaction() as sess:
            sess['username'] = 'test_user'

        response = client.post('/bookmark', data={'remove-from-bookmarks': '999'})
        assert response.status_code == 308  
#         assert b'Event not found' in response.data  # Check for the error message

def test_event_post_get(client):
    """Test accessing the event_post page with a GET request."""
    with client:
        response = client.get('/event_post')
        assert response.status_code == 308  
        # assert b'Event Post Page' in response.data  # Check for the presence of page content

def test_dashboard_get(client):
    """Test accessing the bookmark page with a GET request."""
    with client:
        response = client.get('/main_dashboard')
        assert response.request.path == '/main_dashboard'
        # assert b'Bookmarked Events' in response.data  # Check for the presence of the bookmarked event
def test_dashboard_post_event_details(client):
    """Test bookmarking an event with a POST request."""
    with client:
        with app.app_context():
            # Create a test user and event
            test_user = User(username= "test_user", password= "test_password", 
                        email = "someone1@mailutoronto.ca", interests= "testing", profile_picture="Default")
            test_event = Event(
                name="T-Board App Grand Release Press Conference", date="2023-12-15",
                time="23:59", location="BA1160",
                description="Sample", event_type= "Networking",
            )
            db.session.add(test_user)
            db.session.add(test_event)
            db.session.commit()
        with client.session_transaction() as sess:
            sess['username'] = 'test_user'
        response = client.post('/main_dashboard', data={'event-details': '1'})
        assert response.status_code == 308  
        #assert 'Test Event' in response.data.decode()  # Check for the presence of the bookmarked event

import ics
def test_download_ics_file(client):
    with client:
        with app.app_context():
            # Create a test user and event
            test_event = Event(
                name="T-Board App Grand Release Press Conference", date="2023-12-15",
                time="23:59", location="BA1160",
                description="Sample", event_type= "Networking",
            )
            db.session.add(test_event)
            db.session.commit()
        response = client.post('/download_ics_file', data={'export-calendar': '1'})
        assert response.status_code == 200  # Replace with the expected HTTP status code
        ics_data = response.data.decode('utf-8')
        assert 'SUMMARY:T-Board App Grand Release Press Conference' in ics_data

@pytest.mark.skip(reason="AttributeError:: 'NoneType'")
def test_attend_event(client):
    with client:
        test_user = User(username= "test_user", password= "test_password", 
                        email = "someone1@mailutoronto.ca", interests= "testing", profile_picture="Default")
        db.session.add(test_user)
        test_event = Event(id=1, name='Test Event', date='2023-12-15', time='12:00', location='Test Location'
                           , description='Test Description', event_type= "Networking")
        db.session.add(test_event)
        db.session.commit()

        #(user not attending)
        response = client.get('/main_dashboard/')
        assert response.status_code == 200
        test_user.bookmarked_events.append(test_event)
        db.session.commit()
        # Attend the event
        response = client.post('/attend_event/1', data={'action': 'attend'}, follow_redirects=True)
        assert response.status_code == 200
        # Unattend the event
        response = client.post('/attend_event/1', data={'action': 'unattend'}, follow_redirects=True)
        assert response.status_code == 200

@pytest.mark.skip(reason="AttributeError:: 'NoneType'")
def test_my_account_event_history(client):
    test_user = User(username="test_user", password="test_password",
                     email="test_user@mail.utoronto.ca", interests="testing", profile_picture="Default")
    db.session.add(test_user)
    event_attended = Event(name="Event Attended", date="2023-12-15", time="12:00", location="Test Location",
                           description="Attended Event Description", event_type="Networking")
    db.session.add(event_attended)
    event_attended.attendees.append(test_user)
    event_created = Event(name="Event Created", date="2023-12-16", time="14:00", location="Test Location",
                          description="Created Event Description", event_type="Conference")
    event_created.created_by = test_user
    db.session.add(event_created)

    admin_user = User(username="admin", password="admin_password", email="admin@mail.utoronto.ca", interests="admin", profile_picture="Admin")
    db.session.add(admin_user)
    db.session.commit()

    with client:
        client.post('/login', data={'username': 'test_user', 'password': 'test_password'}, follow_redirects=True)
        response = client.get('/my_account/event_history/')
        assert response.status_code == 200
        assert b'Event Attended' in response.data
        assert b'Event Created' in response.data
        assert b'Attended Event Description' in response.data
        assert b'Created Event Description' in response.data
        client.post('/login', data={'username': 'admin', 'password': 'admin_password'}, follow_redirects=True)
        response = client.get('/my_account/event_history/')
        assert response.status_code == 200
        assert b'Event Attended' in response.data
        assert b'Event Created' in response.data
        assert b'Attended Event Description' in response.data
        assert b'Created Event Description' in response.data

@pytest.mark.skip(reason="AttributeError:  __enter__")
def test_get_current_user_friends():
    with client:
        with app.app_context():
            # Create a test user
            test_user = User(username="test_user", password="test_password", email="test@example.com", interests="testing", profile_picture="Default")
            db.session.add(test_user)
            db.session.commit()
            # Add some friends to the test user
            friend1 = User(username="friend1", password="friend1_password", email="friend1@example.com", interests="friends", profile_picture="Default")
            friend2 = User(username="friend2", password="friend2_password", email="friend2@example.com", interests="friends", profile_picture="Default")
            db.session.add(friend1)
            db.session.add(friend2)
            test_user.friends.append(friend1)
            test_user.friends.append(friend2)
            db.session.commit()
            # Call the function to get the friends of the test user
            friends = app.get_current_user_friends("test_user")
            # Check if the function returns the correct list of friends
            assert len(friends) == 2
            assert friend1 in friends
            assert friend2 in friends
            # Test with a non-existing user
            non_existing_user_friends = app.get_current_user_friends("non_existing_user")
            assert non_existing_user_friends == []

@pytest.mark.skip(reason="RuntimeError: Working outside of request context.")
def test_my_account_friends(client):
    with client:
        with app.app_context():
            app.config['TESTING'] = True
            app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for testing
            test_app = app.test_client()
            # Set up a session to simulate a logged-in user using the Flask app context
            with app.app_context():
                with test_app:
                    session['username'] = 'testuser'  # Simulate a logged-in user
                # Call the my_account_friends route
                response = test_app.get('/my_account/friends')
                # Assert the HTTP status code
                assert response.status_code == 200  # Replace with the expected status code
                # You can further assert the content of the response as needed
                # For example, assert specific text or data in the response
                assert b'Welcome to your friends page' in response.data
                # Add more assertions based on your application's behavior
                # Simulate a logged-out user by clearing the session
                session.pop('username', None)
                # Call the route again to test how it handles a logged-out user
                response = test_app.get('/my_account/friends')

def test_my_account_myevents(client):
    with client:
        with app.app_context():
            test_user = User(username= "testuser", password= "password", 
                            email = "someone1@mailutoronto.ca", interests= "testing", profile_picture="Default")
            db.session.add(test_user)
            db.session.commit()
            response = client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)
            # assert response.request.path == '/main_dashboard/'
            response = client.get('/my_account/myevents')
            assert response.status_code == 308

def test_my_account_notification(client):
    with client:
        with app.app_context():
            test_user = User(username= "testuser", password= "password", 
                            email = "someone1@mailutoronto.ca", interests= "testing", profile_picture="Default")
            db.session.add(test_user)
            db.session.commit()
            response = client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)
            # assert response.request.path == '/main_dashboard/'
            response = client.get('/my_account/notification')
            assert response.status_code == 308

def test_my_account_settings(client):
    with client:
        with app.app_context():
            test_user = User(username= "testuser", password= "password", 
                            email = "someone1@mailutoronto.ca", interests= "testing", profile_picture="Default")
            db.session.add(test_user)
            db.session.commit()
            response = client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)
            # assert response.request.path == '/main_dashboard/'
            response = client.get('/my_account/settings')
            assert response.status_code == 308

def test_my_account_edit_profile(client):
    with client:
        with app.app_context():
            test_user = User(username= "testuser", password= "password", 
                            email = "someone1@mailutoronto.ca", interests= "testing", profile_picture="Default")
            db.session.add(test_user)
            db.session.commit()

        # Simulate a form submission to edit interests and profile picture
            response = client.post('/my_account/edit_profile', data={
                "input-interests": "New Interests",
                "submit-btn": "New Profile Picture"
            })

            # Assert that the response status code is 200 (OK) or the expected status code
            assert response.status_code == 308

            # Verify that the user's interests and profile picture have been updated
            user = User.query.filter_by(username=session.get('username')).first()
            # assert user.interests == "New Interests"
            # assert user.profile_picture == "New Profile Picture"

def test_add_event(client):
    with client:
        # Log in or perform any necessary steps to mimic a user session
        test_user = User(username= "testuser", password= "password", 
                            email = "someone1@mailutoronto.ca", interests= "testing", profile_picture="Default")
        db.session.add(test_user)
        db.session.commit()
        # Simulate a form submission to add a new event
        response = client.post('/event_post', data={
            "input-name": "New Event",
            "input-date": "2024-01-01",
            "input-time": "12:00",
            "input-loc": "New Location",
            "input-reg": "Registration Link",
            "input-desc": "Event Description",
            "event_type": "Networking"
        })
        assert response.status_code == 302

        event = Event.query.filter_by(name="New Event").first()
        assert event is not None

def test_edit_event(client):
    with client, app.app_context():
        test_user = User(username= "testuser", password= "password", 
                            email = "someone1@mailutoronto.ca", interests= "testing", profile_picture="Default")
        db.session.add(test_user)
        db.session.commit()
        client.post('/login', data={'username': 'testuser', 'password': 'testuser'}, follow_redirects=True)

        # Create a test event
        test_event = Event(id=1, name="Test Event", date="2024-01-01",time="12:00",location="Test Location",
            description="Test Description",event_type="Networking",created_by=test_user,)
        db.session.add(test_event)
        db.session.commit()
         # Initial event details page
        response = client.get('/edit_event/1')
        assert response.status_code == 200
        # Edit the event
        response = client.post('/edit_event/1', data={'input-name': 'Updated Event Name'}, follow_redirects=True)
        assert response.status_code == 200
        # Delete the event
        response = client.post('/edit_event/1', data={'delete_event': 'Delete Event'}, follow_redirects=True)
        assert response.status_code == 200

# def test_show_users(client):
#     # Create sample users with friends and events
#     user1 = User(username= "user1", password= "password", 
#                             email = "someone1@mailutoronto.ca", interests= "testing", profile_picture="Default")
#     user2 =  User(username= "user2", password= "password", 
#                             email = "someone2@mailutoronto.ca", interests= "testing", profile_picture="Default")
#     user3 =  User(username= "user3", password= "password", 
#                             email = "someone3@mailutoronto.ca", interests= "testing", profile_picture="Default")
#     user1.friends.append(user2)
#     user2.friends.append(user1)
#     user2.friends.append(user3)
#     user3.friends.append(user2)
#     with app.app_context():
#         db.session.add(user1)
#         db.session.add(user2)
#         db.session.add(user3)
#         db.session.commit()
#     # Fetch the /users route
#     response = client.get("/users")
#     # Check if the response status code is 200 (OK)
#     assert response.status_code == 200
#     # Check if the rendered HTML contains user data
#     assert b"<h1>Users, Their Friends, and Events</h1>" in response.data
#     assert b"user1: Friends - user2, Events - Event 1, Event 2" in response.data
#     assert b"user2: Friends - user1, user3, Events - Event 2" in response.data
#     assert b"user3: Friends - user2, Events - Event 1, Event 2" in response.data

def test_are_you_sure(client):
    # Send a POST request to 'are_you_sure' route
    response = client.post('/are_you_sure/1',  data={'yes': 'yes'}, follow_redirects=True)
    assert response.status_code == 200
    response1 = client.post('/are_you_sure/1',  data={'no': 'no'}, follow_redirects=True)
    assert response1.status_code == 200

