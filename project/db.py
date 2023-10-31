from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

# Configuration
app = Flask(__name__)
basedir = Path(__file__).resolve().parent
USERS_DATABASE = f"sqlite:///{Path(basedir).joinpath('users.db')}"
EVENTS_DATABASE = f"sqlite:///{Path(basedir).joinpath('events.db')}"

app.config.update(
    SQLALCHEMY_DATABASE_URI=EVENTS_DATABASE,
    SQLALCHEMY_BINDS={'users': USERS_DATABASE, 'events': EVENTS_DATABASE},
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
db = SQLAlchemy(app)

# Models
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

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    interests = db.Column(db.String(255), nullable=True)
    friends = db.Column(db.String(255), default="")

    def __repr__(self):
        return '<User {}>'.format(self.username)

# Sample data
sample_users = [
    {"username": "admin", "password": "adminpass", "email": "admin@mail.utoronto.ca", "interests": "Being an administrator"},
    {"username": "a", "password": "password_a", "email": "a@mail.com", "interests": "Interests A", "friends": "b"},
    {"username": "b", "password": "password_b", "email": "b@mail.com", "interests": "Interests B", "friends": "a,c"},
    {"username": "c", "password": "password_c", "email": "c@mail.com", "interests": "Interests C", "friends": "b"}
]

sample_events = [
    {"name": "Tech Conference 2023", "date": "2023-11-20", "time": "09:00", "location": "Silicon Valley Convention Center", "description": "Join industry leaders..."},
    {"name": "Music Festival", "date": "2023-08-15", "time": "12:00", "location": "Central Park, New York", "description": "A celebration of music..."},
    {"name": "Charity Run", "date": "2023-05-01", "time": "07:00", "location": "Los Angeles City Center", "description": "A 5K run to raise funds..."},
    {"name": "Science Fair", "date": "2023-07-10", "time": "10:00", "location": "Science Museum, London", "description": "Engage with scientific discoveries..."}
]

# Database initialization
with app.app_context():
    db.create_all()
    if not Event.query.first():
        db.session.bulk_insert_mappings(Event, sample_events)
    if not User.query.first():
        db.session.bulk_insert_mappings(User, sample_users)
    db.session.commit()
