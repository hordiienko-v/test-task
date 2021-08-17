from flask import Flask, request, render_template
from flask import redirect
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = 'secret'

@app.route("/", methods=["GET"])
def home():
    error = request.args.get("error")

    return render_template("index.html", error=error)

from app.routes import payment_routes
