from flask import Flask, request, render_template
from flask import redirect
import logging
import os


app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("flask_secret", "secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE", "sqlite:///data.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

@app.route("/", methods=["GET"])
def home():
    error = request.args.get("error")
    return render_template("index.html", error=error)

from app.routes import payment_routes
from app.models.payment import Payment
