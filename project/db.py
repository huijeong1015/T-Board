from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from werkzeug.security import generate_password_hash


# Configuration
USERS_DATABASE = "users.db"
EVENTS_DATABASE = "events.db"
basedir = Path(__file__).resolve().parent

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
attendees = db.Table(
    "attendees",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("event_id", db.Integer, db.ForeignKey("events.id"), primary_key=True),
)

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
# Model for events
class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    time = db.Column(db.String(5), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    attendees = db.relationship(
        "User", secondary=attendees, backref=db.backref("events", lazy="dynamic")
    )

    def __repr__(self):
        return f"<Event {self.name}>"


# Model for users
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    interests = db.Column(db.String(255), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    friends = db.relationship(
        "User",
        secondary=user_friends,
        primaryjoin=(user_friends.c.user_id == id),
        secondaryjoin=(user_friends.c.friend_id == id),
        backref=db.backref("friends_ref", lazy="dynamic"),
    )
    bookmarked_events = db.relationship('Event', secondary=saved_events,
                                             backref=db.backref('bookmarked_ref', lazy='dynamic'))  

    def set_password(self, password):
        self.password = generate_password_hash(password)

        

    def __repr__(self):
        return "<User {}>".format(self.username)


sample_events = [
    {
        "name": "Tech Conference 2023",
        "date": "2023-11-20",
        "time": "09:00",
        "location": "Silicon Valley Convention Center",
        "description": "Join industry leaders...",
    },
    {
        "name": "Music Festival",
        "date": "2023-08-15",
        "time": "12:00",
        "location": "Central Park, New York",
        "description": "A celebration of music...",
    },
    {
        "name": "Charity Run",
        "date": "2023-05-01",
        "time": "07:00",
        "location": "Los Angeles City Center",
        "description": "A 5K run to raise funds...",
    },
    {
        "name": "Science Fair",
        "date": "2023-07-10",
        "time": "10:00",
        "location": "Science Museum, London",
        "description": "Engage with scientific discoveries...",
    },
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
        )
        user_a = User(
            username="user_a",
            password=generate_password_hash("password_a"),
            email="a@mail.com",
            interests="Interests A",
        )
        user_b = User(
            username="user_b",
            password=generate_password_hash("password_b"),
            email="b@mail.com",
            interests="Interests B",
        )
        user_c = User(
            username="user_c",
            password=generate_password_hash("password_c"),
            email="c@mail.com",
            interests="Interests C",
        )

        # Setting up friendships
        user_a.friends.append(user_b)  # a and b are friends
        user_b.friends.append(user_a)  # a and b are friends
        user_b.friends.append(user_c)  # b and c are friends


        # Adding users to events
        tech_conference = Event.query.filter_by(name="Tech Conference 2023").first()
        music_festival = Event.query.filter_by(name="Music Festival").first()
        charity_run = Event.query.filter_by(name="Charity Run").first()

        user_a.bookmarked_events.append(music_festival)

        user_a.events.append(tech_conference)
        user_b.events.append(music_festival)
        user_c.events.append(charity_run)
        print(user_a)
        print(user_a)
        db.session.add(admin)
        db.session.add(user_a)
        db.session.add(user_b)
        db.session.add(user_c)

        db.session.commit()
