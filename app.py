from flask import Flask, render_template, request, redirect, jsonify, make_response, url_for
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVC
from joblib import load

import watcher

clf: SVC = load("./ml/out/crop.recommend.joblib")
reg: RandomForestRegressor = load("./ml/out/yield.prediction.joblib")


app = Flask(
    __name__,
    template_folder=Path(".") / "dist",
    static_folder=Path(".") / "dist" / "assets",
    static_url_path="/assets",
)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///kisaan.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    district = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)


@app.route("/dashboard")
# NOTE: since we this isn't a social media app we don't need
def dashboard():
    return "TODO"


@app.route("/")
def landing():
    return render_template("landing.html")


# TODO change /recommend /yield
@app.route("/recommend", methods=["GET", "POST"])
def recommend_result():
    content = request.get_json()
    res = clf.predict([content["data"]])
    print(content, res)
    return make_response(jsonify({"response": int(res[0])}))


@app.route("/yield", methods=["GET", "POST"])
def yield_result():
    content = request.get_json()
    res = reg.predict([content["data"]])
    return make_response(jsonify({"response": res[0]}))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_id = request.form["login_id"]
        password = request.form["password"]
        user = User.query.filter_by(login_id=login_id, password=password).first()
        if user:
            return render_template("success.html")
        else:
            # Handle incorrect login credentials
            return render_template("login.html", error="Invalid login credentials")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        login_id = request.form["login_id"]
        password = request.form["password"]
        district = request.form["district"]
        name = request.form["name"]

        new_user = User(
            login_id=login_id, password=password, district=district, name=name
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("landing"))

    return render_template("signup.html")


@app.route("/home/<int:user_id>")
def home(user_id):
    user = User.query.get(user_id)
    if user:
        return render_template("home.html", user=user)
    else:
        return "User not found", 404


# this is just an example so I don't forget what TODO returns have to be replaced with later on
def TODO_filler(file_loc: str):
    return render_template(file_loc)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    watcher.start()
    app.run(debug=True)
