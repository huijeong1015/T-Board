from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from db import *

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

#login 
@app.route('/', methods=["GET", "POST"])
@app.route('/login/', methods=["GET", "POST"])
def login():
    """User login management"""
    error = None
    if request.method == "POST":
        if request.form["input-id"] != USERNAME:
            error = "Invalid username"
        elif request.form["input-pwd"] != PASSWORD:
            error = "Invalid password"
        else:
            return redirect(url_for("main_dashboard"))
    return render_template('login.html', error=error)

@app.route('/event_details')
def event_details():
    return render_template('event_details.html')

@app.route('/bookmark')
def bookmark():
    return render_template('bookmark.html')

@app.route('/event_post')
def event_post():
    return render_template('event_post.html')

#login 
# @app.route('/login')
# # methods=['GET', 'POST']
# def login():
#     # destination = request.form.get('destination')
#     # if destination == 'main_dashboard' :
#     #     return redirect(url_for('main_dashboard'))
#     # elif destination == 'register' :
#     #     return redirect(url_for('register'))
#     return render_template('login.html')

#main_dashboard


# this does not work for some reason 
@app.route('/main_dashboard/')
def main_dashboard():
    sql = text("SELECT * FROM event;")
    result = db.session.execute(sql)
    return render_template('main_dashboard.html', events=result)
# @app.('/')
@app.route('/search_dashboard', methods=['POST'])
def searchEvent():
    keyword=request.form["input-search"]
    #some error handling before results are used
    results = []
    if keyword:
        results = Event.query.filter(Event.name.contains(keyword)).all()
    print(results)
    return render_template('search_dashboard.html', events=results)
@app.route('/my_account')
def my_account():
    return render_template('my_account.html')

@app.route('/my_account/event_history')
def my_account_event_history():
    return render_template('my_account_eventhistory.html')

@app.route('/my_account/friends')
def my_account_friends():
    return render_template('my_account_friends.html')

@app.route('/my_account/myevents')
def my_account_myevents():
    return render_template('my_account_myevents.html')

@app.route('/my_account/notification')
def my_account_notification():
    return render_template('my_account_notification.html')

@app.route('/my_account/settings')
def my_account_settings():
    return render_template('my_account_settings.html')

# register account methods=['GET', 'POST'],methods=['GET', 'POST']
@app.route('/register')
def register():
    # username = request.form["input-id"]
    # email = request.form["input-email"]
    return render_template('register.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

