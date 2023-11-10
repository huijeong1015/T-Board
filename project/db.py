from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from werkzeug.security import generate_password_hash
import json
from sqlalchemy.sql import func


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
    average_rating = db.Column(db.Integer, nullable=True)
    number_of_attendees = db.Column(db.Integer, nullable=False, default=0)

    # New method to calculate average rating
    def calculate_average_rating(self):
        total_rating = sum(rating.rating for rating in self.event_ratings)
        count_ratings = len(self.event_ratings)
        return total_rating / count_ratings if count_ratings else 0
    
    def update_average_rating(self):
        # Calculate the average rating
        avg_rating = db.session.query(func.avg(Rating.rating)).filter(Rating.event_id == self.id).scalar()
        # Round the average rating to the nearest whole integer and store it
        self.average_rating = int(round(avg_rating)) if avg_rating is not None else 0

    def count_attendees(self):
    # Use a SQLAlchemy query to count attendees associated with this event
        tmpNum = db.session.query(func.count(Attendee.user_id)).filter(Attendee.event_id == self.id).scalar()
        self.number_of_attendees = tmpNum


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
    {"name": "Graduate Open House", "date": "2024-01-08", "time": "16:00", "location": "Zoom meeting", "description": "Are you interested in applying for graduate studies in drama, theatre, and performance studies at the University of Toronto? Attend our online Graduate Open House to find out about our curriculum, program requirements, funding opportunities and extracurricular activities; meet our faculty and staff; and tour our spaces virtually.", "event_type": "Networking"},
    {"name": "Concrete Canoe General Meeting", "date": "2023-05-01", "time": "19:00", "location": "Bahen Centre", "description": "General meeting open to the public", "event_type": "Club"},
    {"name": "MAT188 Tutoring", "date": "2023-07-10", "time": "10:00", "location": "Zoom", "description": "Running through Mat188 homework problems", "event_type": "Tutoring"}, 
    {"name": "Paris 2024 Opening Ceremony Viewing", "date": "2024-07-26", "time": "09:00", "location": "Sandford Fleming Building Basement, ECE Common Room", "reg_link": "https://www.paris2024.org/en/", "description": "And cheer for the Canadian team!", "event_type": "Sports"}, 
    {"name": "T-Board App Grand Release Press Conference", "date": "2023-11-15", "time": "12:00", "location": "#BA1160 Bahen Centre, 40 St. George St.", "reg_link": "https://q.utoronto.ca/courses/324733/assignments/1141725", "description": "And witness the establishment of the almost-greatest event billboard ever made in U of T history!", "event_type": "Club"}, 
    {"name": "Free Frisbee @ Front", "date": "2023-11-13", "time": "17:00", "location": "Front Campus, King's College Cir.", "description": "Enjoy the last bit of the new Front Campus lawn before winter!", "event_type": "Sports"}, 
    {"name": "Celebrating Lunar New Year 2024!", "date": "2024-02-09", "time": "19:00", "location": "Sandford Fleming Building Basement, ECE Common Room", "description": "All can join; wish a happy new year to everyone at U of T!", "event_type": "Club"},
    {"name": "Python Basics for Data Science & Data Manipulation with Python", "date": "2023-11-16", "time": "17:30", "location": "UC 261, 15 King's College Circle", "description": "workshop", "event_type": "Club", "reg_link": "https://docs.google.com/forms/d/e/1FAIpQLSfXfHDoW1j1Ff8Uod_KpFWag9cFCuAcxczNDWhek4_o7ty04w/viewform"}, 
    {"name": "UTWind Controls Team Meeting", "date": "2023-11-16", "time": "18:10", "location": "Myhal arena", "description": "for controls team member", "event_type": "Club"},
    {"name": "Drop-in Tennis", "date": "2023-11-17", "time": "10:00", "location": "Athletic Center", "description": "for detailed schedule in the link", "event_type": "Sports", "reg_link": "https://kpe.utoronto.ca/sport-recreationrecreational-workouts-activitiesdrop-sports-activities/drop-tennis"},
    {"name": "Drop-in Ice Skating", "date": "2023-11-19", "time": "13:00", "location": "Athletic Center", "description": "for detailed schedule in the link", "event_type": "Sports", "reg_link": "https://kpe.utoronto.ca/sport-recreationrecreational-workouts-activitiesdrop-sports-activities/drop-ice-skate"},
    {"name": "ECE344 Exam Jam", "date": "2023-12-07", "time": "09:00", "location": "SF3202, Sandford Fleming Building", "description": "Use this last day to get yourself ready for your very first exam!", "event_type": "Tutoring"},
    {"name": "Celebrate Christmas!", "date": "2023-12-24", "time": "19:00", "location": "ECE Common Room", "description": "Organized individually, available to all. Free cookies and donuts available for pickup!", "event_type": "Club"},
    {"name": "Superbowl Viewing", "date": "2024-02-11", "time": "17:00", "location": "SF Basement, ECE Common Room", "description": "Watch American football with everyone!", "event_type": "Sports"},
    {"name": "Walk @ Nathan Philips Square", "date": "2023-12-07", "time": "19:00", "location": "Chestnut Residence, 88 Chestnut St.", "description": "Have a walk in the annual Cavalcade of Lights and relax yourself before the exam period! All attendees should meet in the lobby.", "event_type": "Other", "reg_link": "https://www.toronto.ca/explore-enjoy/festivals-events/cavalcade-of-lights/"},
    {"name": "Just Machine Learning", "date": "2024-01-22", "time": "11:00", "location": "Data Sciences Institute, 10th floor Seminar Room, 700 University Avenue, Toronto", "description": "Join us for the Data Sciences Speaker Series with Prof. Tina Eliassi-Rad is the inaugural President Joseph E. Aoun Professor at Northeastern University.  This talk is co-sponsored by the Data Sciences Institute and the Centre for Analytics and Artificial Intelligence Engineering (CARTE), University of Toronto.", "event_type": "Networking", "reg_link": "https://www.eventbrite.ca/e/just-machine-learning-prof-tina-eliassi-rad-tickets-736594964367?aff=oddtdtcreator"},
    {"name": "History of Modern Philosophy Group Talk", "date": "2023-12-08", "time": "15:00", "location": "Jackman Humanities Building, Room 418, 170 St. George Street", "description": "The History of Philosophy Group is pleased to welcome as speaker David James Barnett, an associate professor of Philosophy at the University of Toronto who specializes in epistemology and the philosophy of mind.", "event_type": "Networking"},
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
            username="Karl A",
            password=generate_password_hash("password_a"),
            email="a@mail.com",
            interests="Volleyball, Computer Engineering",
            profile_picture="Surprised",
            is_first_login=False
        )
        user_b = User(
            username="Alex B",
            password=generate_password_hash("password_b"),
            email="b@mail.com",
            interests="Literature",
            profile_picture="Happy",
            is_first_login=False
        )
        user_c = User(
            username="Jamie C",
            password=generate_password_hash("password_c"),
            email="c@mail.com",
            interests="Science",
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