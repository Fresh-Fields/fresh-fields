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
from datetime import date

from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVC
import pandas as pd
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
for district in ["Bhiwandi", "Vasai", "Palghar", "Ulhasnagar"]:
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
    print(content)
    labels = [
        "N",
        "P",
        "K",
        "temperature",
        "humidity",
        "ph",
        "rainfall",
        "season",
    ]
    data = {}
    for i in range(len(labels)):
        data[labels[i]] = [content[i]]
    X = pd.DataFrame(data)
    res = clf.predict_proba(X)
    print(res)
    return make_response(jsonify(res.tolist()))


@app.route("/yield", methods=["GET", "POST"])
def yield_result():
    X = [request.get_json()]
    res = np.array(reg.predict(X))
    return make_response(jsonify(res.tolist()))


@app.route("/price/<location>", methods=["POST"])
def price_result(location):
    if location not in price_models:
        return make_response(jsonify({"error": f"Model for {location} not found"}), 404)

    print(f"location: {location}")

    price_model = price_models[location]

    sequence_length = 56

    df = pd.read_csv(f"./ml/data/{location}.Rice.csv")[-56:]

    df.loc[len(df)] = {
        "Price Date": date.today().strftime("%Y-%m-%d"),
        "Modal Price (Rs./Quintal)": df["Modal Price (Rs./Quintal)"].mode(),
    }

    df["Price Date"] = pd.to_datetime(df["Price Date"], format="%Y-%m-%d")
    # complete_dates = pd.date_range(
    #     start=df["Price Date"].min(), end=df["Price Date"].max(), freq="D"
    # )
    # complete_df = pd.DataFrame({"Price Date": complete_dates})
    # df = pd.merge(complete_df, df, on="Price Date", how="left")

    # df["Modal Price (Rs./Quintal)"] = df["Modal Price (Rs./Quintal)"].ffill()

    df.rename(
        columns={"Modal Price (Rs./Quintal)": "Price", "Price Date": "Date"},
        inplace=True,
    )

    df.set_index("Date", inplace=True)
    df.sort_index(inplace=True)
    df.index = pd.to_datetime(df.index)
    df = df[-57:]

    print(df.shape)

    df_tr = price_model.named_steps["scaler"].transform(df)
    X = []

    for i in range(len(df_tr) - sequence_length):
        X.append(df_tr[i : (i + sequence_length)])

    X = np.array(X)

    res = price_model.named_steps["model"].predict(X).reshape(-1, 1)
    res = price_model.named_steps["scaler"].inverse_transform(res)
    res = res.flatten()
    res = np.array(df["Price"][-14:]) + res
    res = [float(i) for i in res.tolist()]
    print(type(res))
    print(res)

    return make_response(jsonify({"prediction": res}))


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
