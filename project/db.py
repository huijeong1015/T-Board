from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

# Configuration
USERS_DATABASE = "users.db"
EVENTS_DATABASE = "events.db"
basedir = Path(__file__).resolve().parent

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
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Event {self.name}>"

# Model for users
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    interests = db.Column(db.String(255), nullable=True)  
    def __repr__(self):
        return '<User {}>'.format(self.username)

sample_users = [
    {"username": "admin", "password": "adminpass", "email": "admin@mail.utoronto.ca", "interests": "Being an administrator"}
]

sample_events = [
    {"name": "Tech Conference 2023", "date": "2023-11-20", "time": "09:00", "location": "Silicon Valley Convention Center", "description": "Join industry leaders..."},
    {"name": "Music Festival", "date": "2023-08-15", "time": "12:00", "location": "Central Park, New York", "description": "A celebration of music..."},
    {"name": "Charity Run", "date": "2023-05-01", "time": "07:00", "location": "Los Angeles City Center", "description": "A 5K run to raise funds..."},
    {"name": "Science Fair", "date": "2023-07-10", "time": "10:00", "location": "Science Museum, London", "description": "Engage with scientific discoveries..."}
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

