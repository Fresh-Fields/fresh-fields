from flask import Flask, render_template, request, jsonify, make_response
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


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test1.db"
app.config["VITE_AUTO_INSERT"] = True

# db = SQLAlchemy(app) # TODO merge Jatin's code


@app.route("/dashboard")
# NOTE: since we this isn't a social media app we don't need
def dashboard():
    return "TODO"


@app.route("/")
def landing():
    return render_template("landing.html")


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


# this is just an example so I don't forget what TODO returns have to be replaced with later on
def TODO_filler(file_loc: str):
    return render_template(file_loc)


if __name__ == "__main__":
    watcher.start()
    app.run(debug=True)
