"""
Kindle can show Microsoft To Do
"""
import base64
from flask import Flask
import io
import qrcode
import uuid

app = Flask(__name__)

temp_token_mappings = {}

@app.route("/")
def index():
    temp_id = uuid.uuid4()
    # TODO: make login

    auth_code_image = qrcode.make("https://www.google.com")
    buffer = io.BytesIO()
    auth_code_image.save(buffer)
    base64_image = base64.b64encode(buffer.getvalue()).decode()
    return '<div style="text-align: center; width: 100%;">' +\
        f'<img src="data:image/png;base64,{base64_image}" alt="Login QR code"></p>' +\
        '<p>请扫码登录您的 Microsoft™ 账号</p>'

@app.route("/auth_callback")
def auth():
    return "Auth callback to get the token"

@app.route("/tasks")
def tasks():
    return "Get tasks"


@app.route("/taskfolders")
def taskfolders():
    return "Get folder"
