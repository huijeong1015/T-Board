from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)

bootstrap = Bootstrap(app)

# class Login(FlaskForm):
#     login_username = StringField('What is your name?', validators=[DataRequired()])
#     login_password = StringField('What is your UofT Email address?', validators=[DataRequired(), Email()])
#     submit = SubmitField('Submit')

#login 
@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/eventdetails')
def eventdetails():
    return render_template('event_details.html')

@app.route('/search')
def search():
    return render_template('search_tab.html')

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
@app.route('/main_dashboard')
def main_dashboard():
    return render_template('main_dashboard.html')

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

# register account
@app.route('/register')
def register():
    return render_template('register.html')

