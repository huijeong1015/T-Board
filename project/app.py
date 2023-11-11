import io
from flask import (
    Flask,
    after_this_request,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    render_template_string,
    send_file,
    request,
    jsonify,
    make_response
)
from datetime import datetime, timedelta
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.sql import func
from project.db import *
from project.register import *
from werkzeug.security import check_password_hash
import re
import ics
import pytz

app.config["SECRET_KEY"] = os.urandom(24)
LIST_OF_EVENT_TYPES = ["Tutoring", "Sports", "Club", "Networking", "Other"] 

#Helper functions
def get_user_interests(username=None):
    if not username:
        username=session.get('username')
    user = User.query.filter_by(username=username).first()
    return user.interests

def get_user_email(username=None):
    if not username:
        username=session.get('username')
    user = User.query.filter_by(username=username).first()
    return user.email

def get_user_profile_picture(username = None):
    if not username:
        username = session.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
            return user.profile_picture
    return "default_profile_picture.jpg"

def get_user(username = None):
    if not username:
        username = session.get('username')
    user = User.query.filter_by(username=username).first()
    return(user)  

def check_password_strength(password):
    length = len(password)
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(not char.isalnum() for char in password)

    if length >= 8 and has_upper and has_lower and has_digit and has_special:
        return "strong"
    elif length >= 6 and has_upper and has_lower and has_digit:
        return "medium"
    else:
        return "weak"

def sort_events_by_date(events, order):
    events_with_dt = [(event, datetime.strptime(f"{event.date} {event.time}", "%Y-%m-%d %H:%M")) for event in events]

    # Sort the events based on the datetime objects
    if order == 'Newest to Oldest':
        sorted_events_with_dt = sorted(events_with_dt, key=lambda x: x[1], reverse=True)
    elif order == 'Oldest to Newest':
        sorted_events_with_dt = sorted(events_with_dt, key=lambda x: x[1])

    sorted_events = [event_with_dt[0] for event_with_dt in sorted_events_with_dt]

    return sorted_events

def sort_events_by_name(events, order):
    if order == 'A to Z':
        sorted_events = sorted(events, key=lambda event: event.name.lower())
    elif order == 'Z to A':
        sorted_events = sorted(events, key=lambda event: event.name.lower(), reverse=True)

    return sorted_events

@app.route("/", methods=["GET", "POST"])
def first_page():
    return redirect(url_for("login"))

@app.route("/login/", methods=["GET", "POST"])
def login():
    if 'username' in session:
        print('we hit this case')
        return redirect(url_for("main_dashboard"))
    
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username:
            error = "Username field is empty."
        elif not password:
            error = "Password field is empty."
        else:
            user = User.query.filter_by(username=username).first()
            if user is None:
                error = f"No \"{username}\" user found. Create a new account."
                flash(error)
            elif not check_password_hash(user.password, password):
                error = "Wrong password. Try again."
                flash(error)
            elif user.is_first_login:
                # Start a user session
                session["username"] = username
                session['user_id'] = user.id
                # User should finish setting up the account
                return redirect(url_for("finish_account_setup"))
            else:
                # Start a user session
                session["username"] = username
                session['user_id'] = user.id
                return redirect(url_for("main_dashboard"))
        
    response = make_response(render_template("login.html", error=error))
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.pop('username', None)
    session.pop('user_id', None)  
    return redirect(url_for('login'))

@app.route("/finish_setup/", methods=["GET", "POST"])
def finish_account_setup():
    username = session.get('username')
    user = User.query.filter_by(username=username).first() 
    error = None
    if request.method == "POST":
        password = request.form["input-pwd"]
        confirm_password = request.form["input-confirm-pwd"]
        interests = request.form["input-interests"]

        # Password strength check
        password_strength = check_password_strength(password)

        # Perform validation checks on the form data
        if password != confirm_password:
            error = "Passwords do not match."
            flash(error)
        elif password_strength != "strong":
            error = f"Password strength is {password_strength}. Please use a stronger password."
            flash(error)
        else:
            user.set_password(password)  # Hash the password
            user.interests = interests
            user.is_first_login = False
            db.session.commit()
            return redirect(url_for("login"))

    return render_template("login_firsttime.html", error=error, user=username)

@app.route("/register/", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form["input-id"]
        email = request.form["input-email"]
        confirm_email = request.form["input-confirm-email"]

        # Check if username or email is already taken
        username_check = User.query.filter_by(username=username).first()
        email_check = User.query.filter_by(email=email).first()

        # Perform validation checks on the form data
        if 'utoronto' not in email:
            error = "Enter University of Toronto email."
            flash(error)
        elif email != confirm_email:
            error = "Emails do not match."
            flash(error)
        elif username_check is not None:
            error = "This Username is taken, please try a different one."
            flash(error)
        elif email_check is not None:
            error = "This email has already been used. Please return to the login page or use a different email."
            flash(error)
        else:
            temp_pwd = generate_temporary_pwd()
            new_user = User(username=username, email=email)
            new_user.set_password(temp_pwd)  # Hash the password
            db.session.add(new_user)
            db.session.commit()
            email_temporary_pwd(email, temp_pwd)
            flash("A temporary password has been sent to your email. Please check.")
            return redirect(url_for("login"))

    return render_template("register.html")
  
@app.route("/bookmark/", methods=["GET", "POST"])
def bookmark():
    error_msg = ""
    username = session.get('username')
    user = User.query.filter_by(username=username).first() 
    print(user)
    bookmarked = user.bookmarked_events

    if request.method == "POST":
        if request.form.get("event-details") != None:
            event_id = int(request.form["event-details"])
            event = Event.query.filter_by(id=event_id).first()
            bookmarked_events_ids = [event.id for event in bookmarked]
            return render_template("event_details.html", event=event, profile_picture=get_user_profile_picture(), bookmarked_events=bookmarked_events_ids, top_right_image=None)   
        if request.form.get("remove-from-bookmarks") != None:
            bookmark_id = int(request.form["remove-from-bookmarks"])
            event_to_remove = Event.query.filter_by(id=bookmark_id).first() 
            if event_to_remove in user.bookmarked_events:
                user.bookmarked_events.remove(event_to_remove)
                bookmarked = user.bookmarked_events
                db.session.commit()
            else:
                error_msg = str(event_to_remove) + "is not associated with this user's bookmarked events"
    return render_template('bookmark.html', bookmarked_events=bookmarked, profile_picture=get_user_profile_picture(), error_msg = error_msg, user=username, top_right_image=None)

@app.route("/event_post/")
def event_post():
    return render_template('event_post.html', profile_picture=get_user_profile_picture(), event_types=event_types, top_right_image=None)

@app.route('/toggle_value', methods=['POST'])
def handle_button_click():
    
    #get the button value and print it
    data = request.get_json()
    bookmark_id = data['value']
    print("the button value is " + bookmark_id)
    #get the user and the username and their bookmarked events
    user = get_user()
    username = user.username
    bookmarked_events = user.bookmarked_events

    #filter the db for the event we need to bookmark and print its value
    event_to_bookmark = Event.query.filter_by(id=bookmark_id).first()
    print(event_to_bookmark)

    is_bookmarked = False    
        
    if event_to_bookmark not in bookmarked_events:
        bookmarked_events.append(event_to_bookmark)
        try:
            db.session.commit()
            response_message = 'Event added to bookmarks.'
            is_bookmarked = True
        except Exception as e:
            db.session.rollback()
            response_message = 'Error adding event to bookmarks.'
    else:
        bookmarked_events.remove(event_to_bookmark)
        try:
            db.session.commit()
            response_message = 'Event removed from bookmarks.'
            is_bookmarked = False
        except Exception as e:
            db.session.rollback()
            response_message = 'Error removing event from bookmarks.'
            print(event)
    if session['show-bookmarked'] == 'show-bookmarked':
        print(session['show-bookmarked'])
        return jsonify( {'redirect': url_for("main_dashboard")})
    return jsonify(success=True, response_message = response_message, added = is_bookmarked)  # Send a response back to the client

@app.route("/filtering/", methods=["GET", "POST"])
def filter_events(searching=False):
    user=get_user()
    error_msg=""
    if  user.event_types_checked == None or user.event_types_checked == '[false]' or user.event_types_checked == '[]':
        event_types_checked = [False] 
        user.set_event_types_checked(event_types_checked)
        db.session.commit()
        sql = text("SELECT * FROM events;")
        filtered_events = db.session.execute(sql)
    else:
        event_types_checked = user.get_event_types_checked()
        filtered_events = []
        for filter in event_types_checked: 
            filtered_events = filtered_events + (Event.query.filter(Event.event_type.contains(filter)).all())
        events = filtered_events 
    print(user)
    if request.method == "POST":
        if not searching:
            if request.form.getlist('filter') != [] and request.form.getlist('reset-filters') == []:
                event_types_checked = request.form.getlist('filter')

                filtered_events = []
                for filter in event_types_checked: 
                    filtered_events = filtered_events + (Event.query.filter(Event.event_type.contains(filter)).all())
            else:
                sql = text("SELECT * FROM events;")
                events = db.session.execute(sql)
                filtered_events = events
                event_types_checked = []
            if len(event_types_checked) > 0 and len(filtered_events) <= 0 :
                error_msg = "Looks like there are no events to show."
    events = filtered_events 
    user.set_event_types_checked(event_types_checked)
    db.session.commit()
    
    return(events, error_msg)

def sort(events, sort_by):
# Sort the events based on what user selected
    if sort_by == "asc-alphabetic":
         events = sort_events_by_name(events, 'A to Z')
    elif sort_by == "desc-alphabetic":
        events = sort_events_by_name(events, 'Z to A')
    elif sort_by == "asc-date":
        events = sort_events_by_date(events, 'Oldest to Newest')
    elif sort_by == "desc-date":  
        events = sort_events_by_date(events, 'Newest to Oldest')   
    return (events)

@app.route('/set_sidetab_state', methods=['POST'])
def set_sidetab_state():
    data = request.get_json()
    session['is_sidetab_visible'] = data['isSidetabVisible']
    return jsonify(success=True)

@app.route("/main_dashboard/", methods=["GET", "POST"])
def main_dashboard():
    sql = text("SELECT * FROM events;")
    events = db.session.execute(sql)
    search_result = []
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    if user.event_types_checked == None:
        user.set_event_types_checked ([])
    bookmarked_events = user.bookmarked_events
    sort_by = request.form.get('sort-by')
    error_msg = ""
    # bookmark_checked =False 
    is_sidetab_visible = session.get('is_sidetab_visible', True)
    if 'show-bookmarked' not in session:
        session['show-bookmarked']='false'
        print(session['show-bookmarked'])
    if 'view_event_details' in session:
        event_id = session.pop('view_event_details', None)
        event = Event.query.filter_by(id=event_id).first()
        attendee_record = Attendee.query.filter_by(user_id=user.id, event_id=event_id).first()
        flag = 'attending' if attendee_record else 'not attending'
        bookmarked_events_ids = [event.id for event in bookmarked_events]
        user_rating = Rating.query.filter_by(user_id=user.id, event_id=event.id).first()
        user_rating_value = user_rating.rating if user_rating else 0 #Base case will be 0

        if attendee_record.notification_preference != -1:
            notification_checked=True
        else:
            notification_checked=False

        # Directly render the event details template
        return render_template("event_details.html", event=event, profile_picture=get_user_profile_picture(), flag=flag,
                               bookmarked_events=bookmarked_events_ids, notification_checked=notification_checked, user_rating=user_rating_value,
                               top_right_image=None)

    if request.method == "POST":
        # Handles event details button
        if request.form.get("event-details") != None:
            event_id = int(request.form["event-details"])
            event = Event.query.filter_by(id=event_id).first()
            username = session.get('username')
            user = User.query.filter_by(username=username).first()
            attendee_record = Attendee.query.filter_by(user_id=user.id, event_id=event_id).first()
            flag = 'attending' if attendee_record else 'not attending'
            bookmarked_events_ids = [event.id for event in bookmarked_events]
            user_rating = Rating.query.filter_by(user_id=user.id, event_id=event.id).first()
            user_rating_value = user_rating.rating if user_rating else 0 #Base case will be 0

            if attendee_record != None and attendee_record.notification_preference !=-1: 
                notification_checked=True
        
            else:
                notification_checked=False

            db.session.commit()
            return render_template("event_details.html", 
                                   event=event, 
                                   profile_picture=get_user_profile_picture(), 
                                   flag=flag, 
                                   bookmarked_events=bookmarked_events_ids, 
                                   notification_checked=notification_checked,
                                   user_rating=user_rating_value,
                                   top_right_image=None)
        
        if request.form.get('reset-filters') != None:
            user.set_event_types_checked([])

        if request.form.get('show-bookmarked') != None:
            session['show-bookmarked'] = request.form.get('show-bookmarked')
            print (request.form.get("show-bookmarked"))
        elif 'input-search' in request.form:
            search_result, error_msg = search_event() 
        else:
            session['show-bookmarked'] = 'false'
            
    if 'input-search' not in request.form:    
        events, error_msg = filter_events()
        events = sort(events, sort_by)
    else:
        events = search_result
        events = sort(events, sort_by)
        if len(events) <= 0:
            keyword = request.form['input-search']
            error_msg = "We couldn't find any matches for \"" + keyword + '".'


    bookmarked_events_ids = [event.id for event in bookmarked_events]
    username=session.get('username')
    if session['show-bookmarked'] == 'show-bookmarked':
        bookmark_checked = True
        bookmarked_evevnts_ids_set = set(bookmarked_events_ids)
        event_ids = [event.id for event in events if event.id not in bookmarked_evevnts_ids_set]
        events = Event.query.filter(Event.id.in_(event_ids)).all()
        if len(events) <= 0 :
            error_msg = "Looks like there are no events to show."
    # session['show-bookmarked'] = bookmark_checked
    else:
        bookmark_checked = False
    
     
    db.session.commit()
    return render_template("main_dashboard.html", 
                           events=events, 
                           profile_picture=get_user_profile_picture(), 
                           error_msg=error_msg, 
                           bookmark_checked=bookmark_checked,
                           bookmarked_events=bookmarked_events_ids, 
                           sort_by=sort_by, 
                           event_types_checked=user.get_event_types_checked(),
                           username=username,
                           list_of_event_types=LIST_OF_EVENT_TYPES,
                           is_sidetab_visible=is_sidetab_visible, top_right_image=None)

@app.route("/main_dashboard/", methods=["POST", "GET"])
def search_event():
    keyword = request.form["input-search"]
    # some error handling before results are used

    results = []
    filtered_events, error_msg = filter_events(searching = True)
    filtered_events_ids = [event.id for event in filtered_events]
    if keyword:
        results = Event.query\
            .filter(Event.name.contains(keyword), Event.id.in_(filtered_events_ids))\
            .all()
        
    return results, error_msg

@app.route('/download_ics_file', methods=['POST'])
def download_ics_file():
    event_id = int(request.form.get('export-calendar'))
    preference = int(request.form.get('preference')) if request.form.get('preference') else None
    event = Event.query.filter_by(id=event_id).first()
    c = ics.Calendar()
    e = ics.Event()
    e.name = event.name
    e.begin = event.date + ' ' + event.time
    e.begin = e.begin.shift(hours=5) #EST
    e.location = event.location
    e.description = event.description
    
    if preference is not None:
        alarm_trigger = timedelta(minutes=-preference)
        alarm = ics.alarm.DisplayAlarm(trigger=alarm_trigger)
        e.alarms.append(alarm)  
    
    c.events.add(e)

    filename = (event.name).strip().replace(' ','') + '.ics'

    # Write the ics file
    with open(os.path.join("project", filename), 'w') as f:
        f.write(c.serialize())

    # Lines to make sure the file gets deleted once the user finishes downloading    
    return_data = io.BytesIO()
    with open(os.path.join("project", filename), 'rb') as f:
        return_data.write(f.read())

    return_data.seek(0)
    os.remove(os.path.join("project", filename))

    # Ask user to download the file
    return send_file(return_data, mimetype="application/ics", download_name=filename, as_attachment=True)

@app.route('/attend_event/<int:event_id>', methods=['POST'])
def attend_event(event_id):
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    bookmarked_events_ids = [event.id for event in user.bookmarked_events]
    event = Event.query.filter_by(id=event_id).first()
    action = request.form.get('action')
    flag = 'not attending' #base case

    # Find existing attendee record
    attendee = Attendee.query.filter_by(user_id=user.id, event_id=event.id).first()
    
    if action == 'attend':
        # If the user is not attending, add them as an attendee
        if not attendee:
            new_attendee = Attendee(user_id=user.id, event_id=event.id, notification_preference='-1')
            db.session.add(new_attendee)
            event.count_attendees()
            db.session.commit()
            flag = 'attending'
    elif action == 'unattend':
        # If the user is attending, remove them as an attendee
        if attendee:
            db.session.delete(attendee)
            event.count_attendees()
            db.session.commit()
            flag = 'not attending'

    db.session.commit()
    return render_template("event_details.html", event=event, profile_picture=get_user_profile_picture(), flag=flag, bookmarked_events=bookmarked_events_ids, top_right_image=None)

@app.route("/<username>/event_history/") #This Function
def my_account_event_history(username):
    # Security check: Make sure the logged-in user is accessing their own event history or the user is an admin.
    logged_in_username = session.get('username')
    if not logged_in_username:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=username).first()
    attendee_records = Attendee.query.filter_by(user_id=user.id).all()

    current_datetime = datetime.now(pytz.timezone('EST'))
    future_events = []
    past_events = []

    for attendee in attendee_records:
        event = attendee.event
        event_datetime_str = f"{event.date} {event.time}"
        event_datetime_dt = datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M").replace(tzinfo=pytz.timezone('EST'))

        if event_datetime_dt > current_datetime:
            future_events.append(event)
        else:
            past_events.append(event)

    past_events = sort_events_by_date(past_events, 'Newest to Oldest')
    future_events = sort_events_by_date(future_events, 'Newest to Oldest')

    return render_template('my_account_eventhistory.html', username=username, 
                           interests=get_user_interests(username), 
                           profile_picture=get_user_profile_picture(username),
                           future_events=future_events, past_events=past_events,
                           top_right_image=session.get('top_right_image'))

def get_current_user_friends(username):
    # Assuming 'db' is your database connection object and 'User' is your user model
    current_user = User.query.filter_by(username=username).first()
    if current_user:
        return current_user.friends  # This depends on how your user's friends are stored/retrieved
    else:
        return []
    
def filter_friends_by_search_term(friends_list, search_term):
    # Convert the search term to lowercase for a case-insensitive search
    search_term = search_term.lower()
    filtered_list = [
        friend for friend in friends_list
        if search_term in friend.username.lower()  # Use attribute access here
    ]
    return filtered_list

@app.route("/<username>/friends/") #This function
def my_account_friends(username):
    # Ensure the user is logged in or handle appropriately if not
    logged_in_username = session.get('username')
    if not logged_in_username:
        # Redirect to login page or handle it however you prefer
        return redirect(url_for('login'))
    
    # Fetch user-specific data
    interests = get_user_interests(username)
    profile_picture = get_user_profile_picture(username)
    friends_list = get_current_user_friends(username)
    
    # Get the list of friend recommendations
    recommendations = get_friend_recommendations(username)

    search_term = request.args.get('search', '')
    if search_term:
        friends_list = filter_friends_by_search_term(friends_list, search_term)

    # Pass everything to the template
    return render_template('my_account_friends.html',  # Make sure the template name matches your setup
                           username=username,
                           interests=interests, 
                           profile_picture=profile_picture,
                           friends=friends_list,
                           recommended_friends=recommendations,
                           top_right_image=session.get('top_right_image'))

@app.route('/add_friend/<username>', methods=['POST'])
def add_friend(username):
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if the user is not logged in
    current_user = User.query.filter_by(username=session['username']).first()
    friend_to_add = User.query.filter_by(username=username).first()
    
    if not friend_to_add:
        #TODO: Add useful message to user here
        return redirect(url_for('my_account_friends', username=session['username']))

    # Add the logic to create a friendship relationship here
    # This will depend on how your database relationships are set up
    current_user.friends.append(friend_to_add)

    db.session.commit()

    # Redirect back to the friend recommendations page or a success page
    return redirect(url_for('my_account_friends', username=session['username']))

@app.route('/remove_friend/<username>', methods=['POST'])
def remove_friend(username):
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if the user is not logged in

    current_user = User.query.filter_by(username=session['username']).first()
    friend_to_remove = User.query.filter_by(username=username).first()
    
    if not friend_to_remove:
        #TODO: Add useful message to user here
        return redirect(url_for('my_account_friends', username=session['username']))

    # Assuming 'friends' is a many-to-many relationship attribute of the 'User' model
    current_user.friends.remove(friend_to_remove)
    
    db.session.commit()

    # Redirect to the friends list or a confirmation page
    return redirect(url_for('my_account_friends', username=session['username']))

@app.route('/add_friend_via_form', methods=['POST'])
def add_friend_via_form():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if the user is not logged in

    friend_username = request.form['friend_username']  # Get the username from the form data
    current_user = User.query.filter_by(username=session['username']).first()
    friend_to_add = User.query.filter_by(username=friend_username).first()

    #Check if friend exists
    if not friend_to_add:
        #TODO: Add useful message to user here
        return redirect(url_for('my_account_friends', username=session['username']))
    
    # Check if the friend is already in the current user's friend list
    if friend_to_add in current_user.friends:
        # TODO: Add message to inform that the user is already a friend
        return redirect(url_for('my_account_friends', username=session['username']))

    # Add the logic to create a friendship relationship here
    current_user.friends.append(friend_to_add)
    db.session.commit()

    # Redirect back to the friend recommendations page or a success page
    return redirect(url_for('my_account_friends', username=session['username']))

@app.route("/<username>/myevents/") #This function
def my_account_myevents(username):
    # It's a good practice to not assume the session username is the same as the one in the URL
    # You can check if the logged-in user is the same as the username in the URL or if the user has special privileges
    logged_in_username = session.get('username')

    # Redirect to the login page if the user is not logged in
    if not logged_in_username:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=username).first()
  
    if username == 'admin':
        events_created_by_user = Event.query.all()
    else:
        events_created_by_user = Event.query.filter_by(created_by_id=user.id).all()

    top_right = request.args.get('top_right')
  
    if top_right:
        top_right_user = User.query.filter_by(username=top_right).first()
        session['top_right_image'] = top_right_user.profile_picture


    return render_template('my_account_myevents.html', 
                           username=username, 
                           interests=get_user_interests(username), 
                           myevents=events_created_by_user, 
                           profile_picture=get_user_profile_picture(username),
                           top_right_image=session.get('top_right_image'))

@app.route('/set_notification', methods=['POST'])
def set_notification():
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    event_id = request.form.get('event_id')
    attendee_record = Attendee.query.filter_by(user_id=user.id, event_id=event_id).first()

    if 'show-notification' in request.form:
        attendee_record.notification_preference = 30 #Default will be 30 minutes
    else:
        attendee_record.notification_preference = -1

    db.session.commit()
    session['view_event_details'] = event_id

    return redirect(url_for('main_dashboard'))

@app.route('/set_rating', methods=['POST'])
def set_rating():
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    event_id = request.form.get('event_id')
    event = Event.query.filter_by(id=event_id).first()
    updated_rating = request.form.get('updated_rating', type=int)

    # Find the rating by this user for this event, or initialize a new one
    rating = Rating.query.filter_by(user_id=user.id, event_id=event_id).first()
    if rating:
        # Update the existing rating
        rating.rating = updated_rating
    else:
        # Create a new rating instance
        rating = Rating(user_id=user.id, event_id=event_id, rating=updated_rating)
        db.session.add(rating)

    #code goes here
    event.update_average_rating()

    db.session.commit()
    session['view_event_details'] = event_id

    return redirect(url_for('main_dashboard')) 

@app.route("/my_account/notification/", methods=['GET', 'POST'])
def my_account_notification():
    user = get_user()
    attendees = Attendee.query.filter_by(user_id=user.id).all()    
 
    notif_events_with_prefs = [{
        'event': attendee.event,
        'notification_preference': attendee.notification_preference
    } for attendee in attendees if attendee.notification_preference != -1]

    if request.method == "POST":
        updated_event_id = request.form.get('updated_event_id')  # Make sure this matches your form input name
        updated_notification = request.form.get('updated_notification')
        attendee_record = Attendee.query.filter_by(user_id=user.id, event_id=updated_event_id).first()
        
        # Update notification preferences based on user input
        if updated_notification == '30-mins':
            attendee_record.notification_preference = 30
        elif updated_notification == '1-hour':
            attendee_record.notification_preference = 60
        elif updated_notification == '1-day':
            attendee_record.notification_preference = 1440 
        elif updated_notification == '1-week':
            attendee_record.notification_preference = 10080
        
        # Commit the changes to the database
        db.session.commit()
        
        # Redirect to refresh the page and see the changes
        return redirect(url_for('my_account_notification'))
    
    if notif_events_with_prefs:
        print(notif_events_with_prefs[0])

    # Render the page with the sorted events and preferences
    return render_template('my_account_notification.html', 
                           username=session.get('username'), 
                           interests=get_user_interests(), 
                           profile_picture=get_user_profile_picture(),
                           notif_events=notif_events_with_prefs,
                           top_right_image=None)

@app.route("/my_account/settings/", methods=["GET", "POST"])
def my_account_settings():
    return render_template('my_account_settings.html', username=session.get('username'), 
                           interests=get_user_interests(), profile_picture=get_user_profile_picture(), top_right_image=None)

@app.route("/my_account/edit_profile/", methods=["GET", "POST"])
def my_account_edit_profile():
    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    # If the request method is POST, process form submission
    if request.method == "POST":
        #Important: Resricting user to only being able to edit interests and profile picture.
        new_interests = request.form["input-interests"]
        new_profile_picture = request.form["submit-btn"]
        
        user.interests = new_interests
        user.profile_picture = new_profile_picture
        db.session.commit()  

    return render_template('my_account_edit_profile.html', username=session.get('username'), 
                           email=get_user_email(), password=session.get('password'), interests=get_user_interests(),
                           profile_picture=get_user_profile_picture(), profile_pics=profile_pic_types, top_right_image=None)

@app.route("/event_post", methods=["POST"])
def add_event():
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    
    event_name= request.form["input-name"]
    event_date= request.form["input-date"]
    event_time= request.form["input-time"]
    event_location= request.form["input-loc"]
    reg_link= request.form["input-reg"]
    event_description= request.form["input-desc"]
    event_type = request.form.get("event_type")

    event_datetime = f"{event_date} {event_time}"
    event_datetime_dt = datetime.strptime(event_datetime, "%Y-%m-%d %H:%M").replace(tzinfo=pytz.timezone('EST'))

    current_datetime = datetime.now(pytz.timezone('EST'))
    print(current_datetime)
    print(event_datetime_dt)
    if event_datetime_dt > current_datetime:
        new_event = Event(name=event_name, date=event_date, time=event_time, location=event_location, reg_link=reg_link,
                      description=event_description, event_type=event_type, created_by=user)
        db.session.add(new_event)
        db.session.commit()
        render_template('event_post.html', profile_picture=get_user_profile_picture(), event_types=event_types, top_right_image=None)
        return redirect(url_for("main_dashboard"))
    else:
        flash("You cannot post a past event. Change your event's date and time.")
        return render_template('event_post.html', profile_picture=get_user_profile_picture(), event_types=event_types, top_right_image=None)

@app.route('/edit_event/<int:event_id>', methods=["GET", "POST"])
def edit_event(event_id):
    # event = Event.query.get(event_id)
    event = db.session.get(Event, event_id)
    if request.method == 'POST':
        if 'finish_edit' in request.form:
            event = Event.query.filter_by(id=event_id).first()
            event.name= request.form["input-name"]

            event.location= request.form["input-loc"]
            event.reg_link= request.form["input-reg"]
            event.description= request.form["input-desc"]
            event.event_type = request.form.get("event_type")

            event_date= request.form["input-date"]
            event_time= request.form["input-time"]
            event_datetime = f"{event_date} {event_time}"
            event_datetime_dt = datetime.strptime(event_datetime, "%Y-%m-%d %H:%M").replace(tzinfo=pytz.timezone('EST'))
            current_datetime = datetime.now(pytz.timezone('EST'))
            if event_datetime_dt > current_datetime:
                event.time= event_time
                event.date= event_date
                db.session.commit()
                return redirect(url_for("my_account_myevents", username=session.get('username')))
            else:
                #TODO: Give useful message to user
                pass

        elif 'delete_event' in request.form:
            return redirect(url_for("are_you_sure", event_id=event_id))

    return render_template('event_edit.html', profile_picture=get_user_profile_picture(), event=event, event_types=event_types, top_right_image=None)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

# DFS Function for Friend Recommendations
def dfs(graph, start, k):
    visited, stack = set(), [(start, 0)]
    recommendations = set()
    while stack:
        vertex, depth = stack.pop()
        if depth <= k and vertex not in visited:
            visited.add(vertex)
            if (
                depth > 0 and vertex not in graph[start]
            ):  # Exclude start user and their direct friends
                recommendations.add(vertex)
            stack.extend((friend, depth + 1) for friend in graph[vertex] - visited)
    return recommendations

def get_friend_recommendations(username, depth=2):
    # Fetch the current user and their friends
    current_user = User.query.filter_by(username=username).first()
    if not current_user:
        return []

    # Initialize the graph with the current user's friends
    user_data = {
        current_user.username: set(friend.username for friend in current_user.friends)
    }

    # Create a list of all users' usernames to initialize the rest of the graph
    all_usernames = [user.username for user in User.query.all()]
    for uname in all_usernames:
        if uname not in user_data:
            user = User.query.filter_by(username=uname).first()
            user_data[uname] = set(friend.username for friend in user.friends)

    # Now you have a graph of all users and their friends, you can run dfs
    recommendations = dfs(user_data, username, depth)

    # Filter out the current user's direct friends from the recommendations
    recommendations.difference_update(user_data[username])

    # Fetch full User objects for each recommendation
    recommended_users = User.query.filter(User.username.in_(recommendations)).all()

    return recommended_users

@app.route("/recommendations")
def friend_recommendations():
    k = int(request.args.get("k", 2))
    users = User.query.all()
    user_data = {
        user.username: set(friend.username for friend in user.friends) for user in users
    }

    recommendations_html = "<ul>"
    for username in user_data:
        recommendations = dfs(user_data, username, k)
        recommendations = (
            recommendations - user_data[username]
        )  # Filter out existing friends
        recommendations_html += (
            f'<li>{username}: Recommendations - {", ".join(recommendations)}</li>'
        )
    recommendations_html += "</ul>"

    return render_template_string(
        f"<h1>Friend Recommendations</h1>{recommendations_html}"
    )

@app.route('/are_you_sure/<int:event_id>', methods=['GET', 'POST'])
def are_you_sure(event_id):
    event = Event.query.filter_by(id=event_id).first()
    event_name = ""
    if event: 
        event_name = event.name
        if request.method == 'POST':
            if 'yes' in request.form:
                db.session.delete(event)
                db.session.commit()
                return redirect(url_for('my_account_myevents', username=session.get('username')))
            elif 'no' in request.form:
                return redirect(url_for('edit_event', event_id=event_id))
    return render_template('are_you_sure.html', event_id=event_id, event_name=event_name, event=event, profile_picture=get_user_profile_picture(), top_right_image=None)
