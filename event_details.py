from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)

bootstrap = Bootstrap(app)

@app.route('/eventdetails')
def eventdetails():
    return render_template('event_details.html')