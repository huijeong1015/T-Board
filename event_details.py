from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)

bootstrap = Bootstrap(app)

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
#main_dashboard

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
# @app.route('/register')
# def register():
#     return render_template('register.html')

