from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    render_template_string,
)
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.sql import func
from project.db import *
from werkzeug.security import check_password_hash
import re


app.config["SECRET_KEY"] = os.urandom(24)


@app.route("/", methods=["GET", "POST"])
@app.route("/login/", methods=["GET", "POST"])
def login():
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
                error = f"No user found with username: {username}"
            elif not check_password_hash(user.password, password):
                error = "Password does not match for the provided username."
            else:
                # Start a user session
                session["username"] = username
                return redirect(url_for("main_dashboard"))

    return render_template("login.html", error=error)


@app.route("/register/", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form["input-id"]
        email = request.form["input-email"]
        confirm_email = request.form["input-confirm-email"]
        password = request.form["input-pwd"]
        confirm_password = request.form["input-confirm-pwd"]
        interests = request.form["input-interests"]

        # Check if username or email is already taken
        username_check = User.query.filter_by(username=username).first()
        email_check = User.query.filter_by(email=email).first()

        # Password strength check
        password_strength = check_password_strength(password)

        # Perform validation checks on the form data
        if (
            not username
            or not email
            or not confirm_email
            or not password
            or not confirm_password
        ):
            error = "All fields are required."
            flash(error)
        elif email != confirm_email:
            error = "Emails do not match."
            flash(error)
        elif password != confirm_password:
            error = "Passwords do not match."
            flash(error)
        elif password_strength != "strong":
            error = f"Password strength is {password_strength}. Please use a stronger password."
            flash(error)
        elif username_check is not None:
            error = "This Username is taken, please try a different one."
            flash(error)
        elif email_check is not None:
            error = "This email has already been used. Please return to the login page or use a different email."
            flash(error)
        else:
            new_user = User(username=username, email=email, interests=interests)
            new_user.set_password(password)  # Hash the password
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))

    return render_template("register.html")


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


@app.route("/bookmark/")
def bookmark():
    return render_template("bookmark.html")


@app.route("/event_post/")
def event_post():
    return render_template("event_post.html", event_types=event_types)


@app.route("/main_dashboard/", methods=["GET", "POST"])
def main_dashboard():
    sql = text("SELECT * FROM events;")
    result = db.session.execute(sql)
    if request.method == "POST":
        if request.form.get("event-details") != None:
            event_id = int(request.form["event-details"])
            event = Event.query.filter_by(id=event_id).first()
            return render_template("event_details.html", event=event.__dict__)
    return render_template("main_dashboard.html", events=result)


@app.route("/search_dashboard/", methods=["POST"])
def searchEvent():
    keyword = request.form["input-search"]
    # some error handling before results are used
    results = []
    if keyword:
        results = Event.query.filter(Event.name.contains(keyword)).all()
    return render_template("main_dashboard.html", events=results)


def get_user_interests():
    username = session.get("username")
    user = User.query.filter_by(username=username).first()
    return user.interests


def get_user_email():
    username = session.get("username")
    user = User.query.filter_by(username=username).first()
    return user.email


@app.route("/my_account/event_history/")
def my_account_event_history():
    return render_template(
        "my_account_eventhistory.html",
        username=session.get("username"),
        interests=get_user_interests(),
    )


@app.route("/my_account/friends/")
def my_account_friends():
    return render_template(
        "my_account_friends.html",
        username=session.get("username"),
        interests=get_user_interests(),
    )


@app.route("/my_account/myevents/")
def my_account_myevents():
    sql = text("SELECT * FROM events;")
    result = db.session.execute(sql)
    return render_template(
        "my_account_myevents.html",
        username=session.get("username"),
        interests=get_user_interests(),
        myevents=result,
    )


@app.route("/my_account/notification/")
def my_account_notification():
    return render_template(
        "my_account_notification.html",
        username=session.get("username"),
        interests=get_user_interests(),
    )


@app.route("/my_account/settings/")
def my_account_settings():
    return render_template(
        "my_account_settings.html",
        username=session.get("username"),
        interests=get_user_interests(),
    )


@app.route("/my_account/edit_profile/")
def my_account_edit_profile():
    return render_template(
        "my_account_edit_profile.html",
        username=session.get("username"),
        email=get_user_email(),
        password=session.get("password"),
        interests=get_user_interests(),
    )


@app.route("/dataset")
def show_events():
    sql = text("SELECT * FROM events;")
    result = db.session.execute(sql)

    # Extracting data from the ResultProxy object
    events = [
        {column: value for column, value in zip(result.keys(), row)} for row in result
    ]

    # You might return events as a string or JSON, or render them in a template
    return str(events)


@app.route("/event_post", methods=["POST"])
def add_event():
    event_name = request.form["input-name"]
    event_date = request.form["input-date"]
    event_time = request.form["input-time"]
    event_location = request.form["input-loc"]
    event_description = request.form["input-desc"]
    new_event = Event(
        name=event_name,
        date=event_date,
        time=event_time,
        location=event_location,
        description=event_description,
    )
    db.session.add(new_event)
    db.session.commit()
    return render_template("event_post.html")


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


@app.route("/users")
def show_users():
    users = User.query.all()
    user_data = {
        user.username: {
            "friends": [friend.username for friend in user.friends],
            "events": [event.name for event in user.events],
        }
        for user in users
    }
    user_list_html = "<ul>"
    for username, data in user_data.items():
        friends = ", ".join(data["friends"]) if data["friends"] else "None"
        events = ", ".join(data["events"]) if data["events"] else "None"
        user_list_html += f"<li>{username}: Friends - {friends}, Events - {events}</li>"
    user_list_html += "</ul>"
    return render_template_string(
        f"<h1>Users, Their Friends, and Events</h1>{user_list_html}"
    )


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


@app.route("/events")
def new_events():
    events = Event.query.all()
    event_data = {
        event.name: [attendee.username for attendee in event.attendees]
        for event in events
    }
    event_list_html = "<ul>"
    for event_name, attendees in event_data.items():
        event_list_html += f'<li>{event_name}: Attendees - {", ".join(attendees) if attendees else "None"}</li>'
    event_list_html += "</ul>"
    return render_template_string(
        f"<h1>Events and Their Attendees</h1>{event_list_html}"
    )
