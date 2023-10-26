import pytest
from pathlib import Path
from project.main import app, db, Event

TEST_DB = "test.db"

@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    # Ensure we're working with a test database and not the main database
    app.config['TESTING'] = True
    app.config['DATABASE'] = BASE_DIR.joinpath(TEST_DB)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"
    
    # Push an application context so we can connect to the database
    with app.app_context():
        db.create_all() # create db
        yield app.test_client() # run tests
        db.drop_all() # remove db

def test_show_events(client):
    # Populate the database with a sample event
    event = Event(name="Sample Event", date="2023-10-15", time="10:00", location="Test Location", description="This is a test event.")
    with app.app_context():
        db.session.add(event)
        db.session.commit()

    # Fetch the show_events route
    response = client.get('/')
    
    # Ensure the sample event is present in the response
    assert "Sample Event", response.data.decode()

def login(client, username, password):
    """Login helper function"""
    return client.post(
        "/login",
        data=dict(username=username, password=password),
        follow_redirects=True,
    )

# Hui: Test the my account page contains user's id and their interests
def test_my_account_page_contains_userinfo(client):
    login(client, app.config['USERNAME'], app.config['PASSWORD'])
    rv = client.get("/my_account/myevents")
    assert "HELLO, {:s}!".format(app.config['USERNAME']).encode() in rv.data
    assert "Interests: {:s}".format(app.config['INTERESTS']).encode() in rv.data
