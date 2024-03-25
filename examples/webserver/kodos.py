"""
Kindle can show Microsoft To Do
"""
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Get qrcode"

@app.route("/auth_callback")
def auth():
    return "Auth callback to get the token"

@app.route("/tasks")
def tasks():
    return "Get tasks"


@app.route("/taskfolders")
def taskfolders():
    return "Get folder"
