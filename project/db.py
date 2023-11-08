from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from werkzeug.security import generate_password_hash
import json

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

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"sqlite:///{Path(basedir).joinpath(EVENTS_DATABASE)}"
app.config["SQLALCHEMY_BINDS"] = {
    "users": f"sqlite:///{Path(basedir).joinpath(USERS_DATABASE)}",
    "events": f"sqlite:///{Path(basedir).joinpath(EVENTS_DATABASE)}",
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Association table for many-to-many relationship between users and events
class Attendee(db.Model):
    __tablename__ = "attendees"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    notification_preference = db.Column(db.Integer, nullable=False, default=-1)

    # Relationships
    user = db.relationship("User", back_populates="events_attending")
    event = db.relationship("Event", back_populates="attendees")

class Rating(db.Model):
    __tablename__ = "ratings"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), primary_key=True)
    rating = db.Column(db.Float, nullable=False)

    # Relationships using back_populates, with the overlaps keyword
    user = db.relationship("User", back_populates="user_ratings", overlaps="user_ratings")
    event = db.relationship("Event", back_populates="event_ratings", overlaps="event_ratings")

# Association table for self-referential many-to-many relationship (friends)
user_friends = db.Table(
    "user_friends",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("friend_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
)
#Association table between users and events they want to save for later
saved_events = db.Table(
    'saved_events',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True),
)

# Types of events users can select
event_types = [
    {"name": "Networking"},
    {"name": "Sports"},
    {"name": "Tutoring"},
    {"name": "Club"},
    {"name": "Other"},
]

# Model for events
#Current supported event types: ["Tutoring", "Sports", "Club", "Networking", "Other"] 
class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    reg_link = db.Column(db.String(200), nullable=True) 
    description = db.Column(db.Text, nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    attendees = db.relationship('Attendee', back_populates='event')
    event_ratings = db.relationship("Rating", back_populates="event")

    # New method to calculate average rating
    def calculate_average_rating(self):
        total_rating = sum(rating.rating for rating in self.event_ratings)
        count_ratings = len(self.event_ratings)
        return total_rating / count_ratings if count_ratings else 0

    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.relationship('User', back_populates='created_events')
    def __repr__(self):
        return f"<Event {self.name}>"
    
profile_pic_types = [
    {"name": "Default"},
    {"name": "Surprised"},
    {"name": "LaughingCrying"},
    {"name": "Laughing"},
    {"name": "Happy"},
    {"name": "Excited"},
    {"name": "Cool"},
]

# Model for users
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    is_first_login = db.Column(db.Boolean, nullable=False, default=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    interests = db.Column(db.String(255), nullable=False, default="")
    profile_picture = db.Column(db.String(100), nullable=False, default="default")
    event_types_checked = db.Column(db.Text)
    user_ratings = db.relationship("Rating", back_populates="user")
    friends = db.relationship(
        "User",
        secondary=user_friends,
        primaryjoin=(user_friends.c.user_id == id),
        secondaryjoin=(user_friends.c.friend_id == id),
        backref=db.backref("friends_ref", lazy="dynamic"),
    )
    created_events = db.relationship('Event', back_populates='created_by', lazy='dynamic')
    bookmarked_events = db.relationship('Event', secondary=saved_events,
                                             backref=db.backref('bookmarked_ref', lazy='dynamic'))  
    events_attending = db.relationship('Attendee', back_populates='user')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def set_event_types_checked(self, items_list):
        self.event_types_checked = json.dumps(items_list)

    def get_event_types_checked(self):
        return json.loads(self.event_types_checked)    
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

sample_events = [
    {"name": "Tech Conference 2023", "date": "2023-11-20", "time": "09:00", "location": "Silicon Valley Convention Center", "description": "Join industry leaders...", "event_type": "Networking"},
    {"name": "Music Festival", "date": "2023-08-15", "time": "12:00", "location": "Central Park, New York", "description": "A celebration of music...", "event_type": "Other"},
    {"name": "Concrete Canoe General Meeting", "date": "2023-05-01", "time": "07:00", "location": "Bahen Centre", "description": "General meeting open to the public", "event_type": "Club"},
    {"name": "MAT188 Tutoring", "date": "2023-07-10", "time": "10:00", "location": "Zoom", "description": "Running through Mat188 homework problems", "event_type": "Tutoring"}, 
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

    # Populate users table, set up friendships, and add users to events
    if not User.query.first():
        admin = User(
            username="admin",
            password=generate_password_hash("adminpass"),
            email="admin@mail.utoronto.ca",
            interests="Being an administrator",
            profile_picture="Admin",
            is_first_login=False
        )
        user_a = User(
            username="user_a",
            password=generate_password_hash("password_a"),
            email="a@mail.com",
            interests="Interests A",
            profile_picture="Default",
            is_first_login=False
        )
        user_b = User(
            username="user_b",
            password=generate_password_hash("password_b"),
            email="b@mail.com",
            interests="Interests B",
            profile_picture="Happy",
            is_first_login=False
        )
        user_c = User(
            username="user_c",
            password=generate_password_hash("password_c"),
            email="c@mail.com",
            interests="Interests C",
            profile_picture="Cool",
            is_first_login=False
        )

        # Setting up friendships
        user_a.friends.append(user_b)  # a and b are friends
        user_b.friends.append(user_a)  # a and b are friends
        user_b.friends.append(user_c)  # b and c are friends

        # Adding users to events
        tech_conference = Event.query.filter_by(name="Tech Conference 2023").first()
        music_festival = Event.query.filter_by(name="Music Festival").first()
        MAT188 = Event.query.filter_by(name="MAT188 Tutoring").first()

        db.session.add(admin)
        db.session.add(user_a)
        db.session.add(user_b)
        db.session.add(user_c)

        db.session.commit()