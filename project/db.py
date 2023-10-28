from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # Correct import for 'text'
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from pathlib import Path

# configuration
DATABASE="events.db"
USERNAME = "test"
PASSWORD = "ece444test"
INTERESTS = "Computer Engineering"

basedir = Path(__file__).resolve().parent

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{Path(basedir).joinpath(DATABASE)}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Event {self.name}>"

sample_events = [
    {"name": "Tech Conference 2023", "date": "2023-11-20", "time": "09:00", "location": "Silicon Valley Convention Center", "description": "Join industry leaders..."},
    {"name": "Music Festival", "date": "2023-08-15", "time": "12:00", "location": "Central Park, New York", "description": "A celebration of music..."},
    {"name": "Charity Run", "date": "2023-05-01", "time": "07:00", "location": "Los Angeles City Center", "description": "A 5K run to raise funds..."},
    {"name": "Science Fair", "date": "2023-07-10", "time": "10:00", "location": "Science Museum, London", "description": "Engage with scientific discoveries..."}
]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)


with app.app_context():
    db.create_all()
    
    if User.query.first() is None:
        user = User(username='admin', password='adminpass')  # Setting password directly
        db.session.add(user)
    
    if Event.query.first() is None:
        for event_data in sample_events:
            event = Event(**event_data)
            db.session.add(event)

    db.session.commit()




