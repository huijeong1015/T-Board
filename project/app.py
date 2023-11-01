from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.sql import func
from project.db import *
import random #Temporary until we link event type frontend -> backend 

#List of supported event types
event_types = ["Tutoring", "Sports", "Club", "Networking", "Other"]  

#List of supported profile picture: 
Profile_pictures = ["default", "Surprised", "LaughingCrying", "Laughing", "Happy", "Excited", "Cool"]

# #Helper function that gets the current user
# def current_user(attribute='id'):
#     if(attribute == 'id'):
#        username=session.get('username')
#        user = User.query.filter_by(username=username).first
#        return user
#     elif(attribute == 'name'):
#        username=session.get('username')
#        return username

#Temp helper functions
def get_user_interests():
    username=session.get('username')
    user = User.query.filter_by(username=username).first()
    return user.interests

def get_user_email():
    username=session.get('username')
    user = User.query.filter_by(username=username).first()
    return user.email

def get_user_profile_picture():
    username=session.get('username')
    user = User.query.filter_by(username=username).first()
    return user.profile_picture

app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/', methods=["GET", "POST"])
@app.route('/login/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username:
            error = 'Username field is empty.'
        elif not password:
            error = 'Password field is empty.'
        else:
            user = User.query.filter_by(username=username).first()
            if user is None:
                error = f'No user found with username: {username}'
            elif user.password != password:  # Directly comparing the plaintext password
                error = 'Password does not match for the provided username.'
            else:
                # Start a user session
                session['username'] = username
                session['user_id'] = user.id
                return redirect(url_for('main_dashboard'))

    return render_template('login.html', error=error)
    
@app.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    print("We are registering")
    if request.method == 'POST':
        username = request.form['input-id']
        email = request.form['input-email']
        confirm_email = request.form['input-confirm-email']
        password = request.form['input-pwd']
        confirm_password = request.form['input-confirm-pwd']
        interests = request.form['input-interests']

        username_check = User.query.filter_by(username=username).first()
        email_check = User.query.filter_by(email=email).first()

        # Perform validation checks on the form data
        if not username or not email or not confirm_email or not password or not confirm_password:
            error = 'All fields are required.'
            flash(error)
        elif email != confirm_email:
            error = 'Emails do not match.'
            flash(error)
        elif password != confirm_password:
            error = 'Passwords do not match.'
            flash(error)
        elif username_check is not None:
            error = 'This Username is taken, please try a different one.'  
            flash(error)
        elif email_check is not None:
            error = 'This email has already been used. Please return to the login page or use a different email'
            flash(error)
        else:
            #TODO: Need to send email verification
            new_user = User(username=username, password=password, email=email, interests=interests, profile_picture = "default") 
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/bookmark/')
def bookmark():
    return render_template('bookmark.html', profile_picture=get_user_profile_picture())

@app.route('/event_post/')
def event_post():
    return render_template('event_post.html', profile_picture=get_user_profile_picture())

@app.route('/main_dashboard', methods=['GET', 'POST'])
def main_dashboard():
    sql = text("SELECT * FROM events;")
    result = db.session.execute(sql)
    if request.method == "POST":
        if request.form.get('event-details') != None:
            event_id = int(request.form['event-details'])
            event = Event.query.filter_by(id=event_id).first()
            return render_template('event_details.html', event=event.__dict__, profile_picture=get_user_profile_picture())
        if request.form.get('bookmark') != None:
            bookmark_id = int(request.form['bookmark'])
            event_to_bookmark = Event.query.filter_by(id=bookmark_id).first()
            print(bookmark_id)
            username = session.get('username')
            # current_user_id = session['user_id']
            # print(current_user_id)
            user = User.query.filter_by(username=username)
            print(user)
            user.bookmarked_events.append(event_to_bookmark)
            # current_user_id.bookmarked_events.append(bookmark_id)
            # if no work try printing the events being queried in the db.py file
    return render_template('main_dashboard.html', events=result, profile_picture=get_user_profile_picture())

@app.route('/search_dashboard/', methods=['POST'])
def searchEvent():
    keyword=request.form["input-search"]
    #some error handling before results are used
    results = []
    if keyword:
        results = Event.query.filter(Event.name.contains(keyword)).all()
    return render_template('main_dashboard.html', events=results, profile_picture=get_user_profile_picture())

@app.route('/my_account/event_history/')
def my_account_event_history():
    return render_template('my_account_eventhistory.html', username=session.get('username'), 
                           interests=get_user_interests(), profile_picture=get_user_profile_picture())

@app.route('/my_account/friends/')
def my_account_friends():
    return render_template('my_account_friends.html', username=session.get('username'), 
                           interests=get_user_interests(), profile_picture=get_user_profile_picture())

@app.route('/my_account/myevents/')
def my_account_myevents():
    sql = text("SELECT * FROM events;")
    result = db.session.execute(sql)
    return render_template('my_account_myevents.html', username=session.get('username'), interests=get_user_interests(), 
                           myevents=result, profile_picture=get_user_profile_picture())

@app.route('/my_account/notification/')
def my_account_notification():
    return render_template('my_account_notification.html', username=session.get('username'), 
                           interests=get_user_interests(), profile_picture=get_user_profile_picture())

@app.route('/my_account/settings/')
def my_account_settings():
    return render_template('my_account_settings.html', username=session.get('username'), 
                           interests=get_user_interests(), profile_picture=get_user_profile_picture())

@app.route('/my_account/edit_profile/')
def my_account_edit_profile():
    return render_template('my_account_edit_profile.html', username=session.get('username'), 
                           email=get_user_email(), password=session.get('password'), interests=get_user_interests(),
                           profile_picture=get_user_profile_picture())

@app.route('/dataset')
def show_events():
    sql = text("SELECT * FROM events;")
    result = db.session.execute(sql)
    
    # Extracting data from the ResultProxy object
    events = [{column: value for column, value in zip(result.keys(), row)} for row in result]

    # You might return events as a string or JSON, or render them in a template
    return str(events)

@app.route('/users')
def show_users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/event_post', methods=['POST'])
def add_event():
    event_name= request.form["input-name"]
    event_date= request.form["input-date"]
    event_time= request.form["input-time"]
    event_location= request.form["input-loc"]
    event_description= request.form["input-desc"]

    #TEMP: Random event type assigned to new events. remove once front end is complete
    new_event = Event(name=event_name, date=event_date, time=event_time, location=event_location, description=event_description, event_type=random.choice(event_types))
    db.session.add(new_event)
    db.session.commit()
    return render_template('event_post.html', profile_picture=get_user_profile_picture())

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/users')
def users():
    print('hellooooo')
    all_users = User.query.all()
    print("users")

    return render_template('show_users.html', users=all_users)
