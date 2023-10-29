from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

# Configuration
USERS_DATABASE = "users.db"
EVENTS_DATABASE = "events.db"
basedir = Path(__file__).resolve().parent

# Delete the databases if they exist
users_db_path = basedir.joinpath(USERS_DATABASE)
events_db_path = basedir.joinpath(EVENTS_DATABASE)

if users_db_path.exists():
    users_db_path.unlink()

if events_db_path.exists():
    events_db_path.unlink()

# Setting up Flask app instance
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{Path(basedir).joinpath(EVENTS_DATABASE)}"
app.config['SQLALCHEMY_BINDS'] = {
    'users': f"sqlite:///{Path(basedir).joinpath(USERS_DATABASE)}",
    'events': f"sqlite:///{Path(basedir).joinpath(EVENTS_DATABASE)}"
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model for events
#Current supported event types: ["Tutoring", "Sports", "Club", "Networking", "Other"] 
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    bookmarked = db.Column(db.Boolean, default=False)
    event_type = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Event {self.name}>"

# Model for users
#Current support profile picture: ["Default", "Surprised", "LaughingCrying", "Laughing", "Happy", "Excited", "Cool"]
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    interests = db.Column(db.String(255), nullable=True)
    profile_picture = db.Column(db.String(100), nullable=False)
    def __repr__(self):
        return '<User {}>'.format(self.username)

sample_users = [
    {"username": "admin", "password": "adminpass", "email": "admin@mail.utoronto.ca", "interests": "Being an administrator","profile_picture": "Admin" }
]

sample_events = [
    {"name": "Tech Conference 2023", "date": "2023-11-20", "time": "09:00", "location": "Silicon Valley Convention Center", "description": "Join industry leaders...", "event_type": "Networking"},
    {"name": "Music Festival", "date": "2023-08-15", "time": "12:00", "location": "Central Park, New York", "description": "A celebration of music...", "event_type": "Other"},
    {"name": "Concrete Canoe General Meeting", "date": "2023-05-01", "time": "07:00", "location": "Bahen Centre", "description": "General meeting open to the public", "event_type": "Club"},
    {"name": "MAT188 Tutoring", "date": "2023-07-10", "time": "10:00", "location": "Zoom", "description": "Running through Mat188 homework problems", "event_type": "Tutoring"}
]

with app.app_context():
    # Create tables
    db.create_all()

    # Populate events table
    if not Event.query.first():
        for event_data in sample_events:
            event = Event(**event_data)
            db.session.add(event)
        db.session.commit()  

    # Populate users table
    if not User.query.first():
        for user_data in sample_users:
            user = User(**user_data)
            db.session.add(user)
        db.session.commit() 

