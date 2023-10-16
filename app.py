from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # Correct import for 'text'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
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

with app.app_context():
    db.create_all()


sample_events = [
    {"name": "Tech Conference 2023", "date": "2023-11-20", "time": "09:00", "location": "Silicon Valley Convention Center", "description": "Join industry leaders..."},
    {"name": "Music Festival", "date": "2023-08-15", "time": "12:00", "location": "Central Park, New York", "description": "A celebration of music..."},
    {"name": "Charity Run", "date": "2023-05-01", "time": "07:00", "location": "Los Angeles City Center", "description": "A 5K run to raise funds..."},
    {"name": "Science Fair", "date": "2023-07-10", "time": "10:00", "location": "Science Museum, London", "description": "Engage with scientific discoveries..."}
]

with app.app_context():
    if Event.query.first() is None:
        for event_data in sample_events:
            event = Event(**event_data)
            db.session.add(event)
        db.session.commit()

@app.route('/')
def show_events():
    sql = text("SELECT * FROM event;")
    result = db.session.execute(sql)
    
    # Extracting data from the ResultProxy object
    events = [{column: value for column, value in zip(result.keys(), row)} for row in result]

    # You might return events as a string or JSON, or render them in a template
    return str(events)

if __name__ == "__main__":
    app.run(debug=True)
