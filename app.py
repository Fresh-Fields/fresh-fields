from flask import Flask
from flask import render_template
from pathlib import Path
import db

app = Flask(
    __name__,
    template_folder=Path(".") / "dist",
    static_folder=Path(".") / "dist" / "assets",
    static_url_path="/assets",
)


@app.route("/")
def landing():
    return render_template("index.html")


@app.route("/dashboard")
# NOTE: since we this isn't a social media app we don't need
def dashboard():
    return "TODO"


# this is just an example so I don't forget what TODO returns have to be replaced with later on
def TODO_filler(file_loc: str):
    return render_template(file_loc)


app.run(debug=True)
