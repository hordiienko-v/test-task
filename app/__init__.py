from flask import Flask, request, render_template
from flask import redirect
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    if request.method == "GET":
        return render_template("index.html")

from app.routes import payment_routes
