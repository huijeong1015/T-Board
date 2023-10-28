from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from project.db import *

# app = Flask(__name__)
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
# # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] =\
#         'sqlite:///' + os.path.join(basedir, 'events.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# bootstrap = Bootstrap(app)
# db = SQLAlchemy(app)
# class Login(FlaskForm):
#     login_username = StringField('What is your name?', validators=[DataRequired()])
#     login_password = StringField('What is your UofT Email address?', validators=[DataRequired(), Email()])
#     submit = SubmitField('Submit')


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
                # Here you should start a user session
                return redirect(url_for('main_dashboard'))

    return render_template('login.html', error=error)


@app.route('/bookmark/')
def bookmark():
    return render_template('bookmark.html')

@app.route('/event_post/')
def event_post():
    return render_template('event_post.html')

@app.route('/main_dashboard/', methods=['GET', 'POST'])
def main_dashboard():
    sql = text("SELECT * FROM event;")
    result = db.session.execute(sql)
    if request.method == "POST":
        event_id = int(request.form['event-details'])
        event = Event.query.filter_by(id=event_id).first()
        return render_template('event_details.html', event=event.__dict__)
    return render_template('main_dashboard.html', events=result)

# @app.('/')
@app.route('/search_dashboard/', methods=['POST'])
def searchEvent():
    keyword=request.form["input-search"]
    #some error handling before results are used
    results = []
    if keyword:
        results = Event.query.filter(Event.name.contains(keyword)).all()
    return render_template('search_dashboard.html', events=results)

@app.route('/my_account/event_history/')
def my_account_event_history():
    return render_template('my_account_eventhistory.html', username=app.config["USERNAME"], interests=app.config["INTERESTS"])

@app.route('/my_account/friends/')
def my_account_friends():
    return render_template('my_account_friends.html', username=app.config["USERNAME"], interests=app.config["INTERESTS"])

@app.route('/my_account/myevents/')
def my_account_myevents():
    sql = text("SELECT * FROM event;")
    result = db.session.execute(sql)
    return render_template('my_account_myevents.html', username=app.config["USERNAME"], interests=app.config["INTERESTS"], myevents=result)

@app.route('/my_account/notification/')
def my_account_notification():
    return render_template('my_account_notification.html', username=app.config["USERNAME"], interests=app.config["INTERESTS"])

@app.route('/my_account/settings/')
def my_account_settings():
    return render_template('my_account_settings.html', username=app.config["USERNAME"], interests=app.config["INTERESTS"])

@app.route('/dataset')
def show_events():
    sql = text("SELECT * FROM event;")
    result = db.session.execute(sql)
    
    # Extracting data from the ResultProxy object
    events = [{column: value for column, value in zip(result.keys(), row)} for row in result]

    # You might return events as a string or JSON, or render them in a template
    return str(events)

@app.route('/users')
def show_users():
    users = User.query.all()
    return render_template('users.html', users=users)

# @app.route('/event_post', methods=['POST'])
# def event_post_data(): 
#     return
@app.route('/event_post', methods=['POST'])
def add_event():
    # event_name = request.form.get('name')  
    # if event_name:
    event_name= request.form["input-name"]
    event_date= request.form["input-date"]
    event_time= request.form["input-time"]
    event_location= request.form["input-loc"]
    event_description= request.form["input-desc"]
    new_event = Event(name= event_name, date =event_date, time= event_time, location= event_location, description= event_description)
    db.session.add(new_event)
    db.session.commit()
    return render_template('event_post.html')
    # return 'Event added successfully!'
    # return 'Name is required!'
    
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
            print(1)
            error = 'All fields are required.'
        elif email != confirm_email:
            print(2)
            error = 'Emails do not match.'
        elif password != confirm_password:
            print(3)
            error = 'Passwords do not match.'
        elif username_check is not None:
            error = 'This Username is taken, please try a different one.'  
        elif email_check is not None:
            error = 'This email has already been used. Please return to the login page or use a different email'
        else:
            #TODO: Need to send email verification
            print(4)
            new_user = User(username=username, password=password, email=email) 
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html', error=error)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

