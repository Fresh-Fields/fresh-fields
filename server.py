from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route("/")
# TODO: if logged in make this conditional
def landing_or_dashboard():
    return "TODO"


@app.route("/dashboard")
# NOTE: since we this isn't a social media app we don't need
def dashboard():
    return "TODO"


# this is just an example so I don't forget what TODO returns have to be replaced with later on
def TODO_filler(file_loc: str):
    return render_template(file_loc)
