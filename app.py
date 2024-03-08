from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    make_response,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVC
import json

import numpy as np

from keras.layers import Dense, LSTM
from keras.models import Sequential
from joblib import load
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline

import watcher

clf: SVC = load("./ml/out/crop.recommend.joblib")
reg: RandomForestRegressor = load("./ml/out/yield.prediction.joblib")

price_models = {}
for district in ["Nagpur", "Bhiwandi", "Vasai", "Palghar", "Ulhasnagar"]:
    price_models[district]: Pipeline = load(f"./ml/out/forecast.LSTM.{district}.joblib")

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
    phone = db.Column(db.Integer, primary_key=True)
    district = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/home")
def mlpage():
    return render_template("home.html")


@app.route("/ml/recommend")
def recommendation_page():
    return render_template("crop.html")


@app.route("/ml/yield")
def yield_page():
    return render_template("yield.html")


@app.route("/ml/market")
def price_page():
    return render_template("forecast.html")


@app.route("/recommend", methods=["GET", "POST"])
def recommend_result():
    content = request.get_json()
    res = clf.predict_proba([content])
    return make_response(jsonify(res.tolist()))


@app.route("/yield", methods=["GET", "POST"])
def yield_result():
    content = request.get_json()
    res = reg.predict([content["data"]])
    return make_response(jsonify({"response": res[0]}))


@app.route("/price/<location>", methods=["POST"])
def price_result(location):
    if location not in price_models:
        return make_response(jsonify({"error": f"Model for {location} not found"}), 404)

    price_model = price_models[location]

    sequence_length = 56
    content = request.get_json()

    df = content

    df_tr = price_model.named_steps["scaler"].transform(np.array(df).reshape(-1, 1))

    X = []

    for i in range(len(df_tr) - sequence_length):
        X.append(df_tr[i : (i + sequence_length)])

    X = np.array(X)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    res = price_model.predict(X)
    res = (
        price_model.named_steps["scaler"]
        .inverse_transform(res.reshape(-1, 1))
        .flatten()
    )

    return make_response(jsonify({"prediction": res.tolist()}))


# @app.route("/price/<str:location>", methods=["GET", "POST"])
# def price_result(location: str):
#     X = []
#     sequence_length = 56
#     content = request.get_json()
#     df = content
#     df_tr = price_scaler.fit_transform(np.array(df).reshape(-1, 1))

#     for i in range(len(df_tr) - sequence_length):
#         X.append(df_tr[i : (i + sequence_length)])

#     X = np.array(X)
#     X = X.reshape(
#         (
#             X.shape[0],
#             X.shape[1],
#         )
#     )
#     res = price_scaler.inverse_transform(price.predict(X)).flatten()

#     return make_response(json.dumps(res.tolist()[-1]))


@app.route("/login", methods=["POST"])
def login():
    data = json.loads(request.data)
    phone = data["phone"]
    password = data["password"]
    user = User.query.filter_by(phone=phone, password=password).first()
    return jsonify({"success": True}) if user else jsonify({"success": False})


@app.route("/signup", methods=["POST"])
def signup():
    data = json.loads(request.data)
    phone = data["phone"]
    password = data["password"]
    district = data["district"]

    new_user = User(
        phone=int(phone),
        district=int(district),
        password=password,
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"success": True})


@app.route("/userdata/<int:user_id>")
def home(user_id):
    user: User = User.query.get(user_id)
    if user:
        return make_response(user.as_dict())
    else:
        return jsonify(404)


# I wrote this function at like 1AM I think
# so I'm going to keep it but have no clue what it does
# this is just an example so I don't forget what TODO returns have to be replaced with later on
def TODO_filler(file_loc: str):
    return render_template(file_loc)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    watcher.start()
    app.run(debug=True)
