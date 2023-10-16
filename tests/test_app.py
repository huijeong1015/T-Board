import unittest
from app import app, db, Event

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        # Ensure we're working with a test database and not the main database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['TESTING'] = True
        self.app = app.test_client()
        
        # Push an application context so we can connect to the database
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.drop_all()

class FlaskAppTests(BaseTestCase):

    def test_show_events(self):
        # Populate the database with a sample event
        event = Event(name="Sample Event", date="2023-10-15", time="10:00", location="Test Location", description="This is a test event.")
        with app.app_context():
            db.session.add(event)
            db.session.commit()

        # Fetch the show_events route
        response = self.app.get('/')
        
        # Ensure the sample event is present in the response
        self.assertIn("Sample Event", response.data.decode())

if __name__ == "__main__":
    unittest.main()
