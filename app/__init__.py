from flask import Flask, request, render_template
from flask import redirect
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("index.html")
    else:
        pass

@app.route("/pay", methods=["POST"])
def pay():
    pass

@app.route("/bill", methods=["POST"])
def bill():
    pass

@app.route("/invoice", methods=["POST"])
def invoice():
    pass
