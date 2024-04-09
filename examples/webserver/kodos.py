"""
Kindle can show Microsoft To Do
"""
import base64
from flask import Flask, request, jsonify
import io
import qrcode
import msal

from mstodo import constant
from .env import CLIENT_SERCERT

app = Flask(__name__)
ms_app = msal.PublicClientApplication(client_id=constant.MS_AZURE_CLIENT_ID, app_name="InokiToDo")

temp_token_mappings = {}
temp_res_mappings = {}

@app.route("/")
def index():
    # Make login
    callback_url = f"{request.host_url if 'http://' not in request.host_url else request.host_url.replace('127.0.0.1', 'localhost')}auth_callback"
    auth_code_flow = ms_app.initiate_auth_code_flow(
        scopes=constant.MS_TODO_SCOPE,
        redirect_uri=callback_url,
    )
    temp_token_mappings.update({auth_code_flow["state"]: auth_code_flow})
    url = auth_code_flow["auth_uri"]
    auth_code_image = qrcode.make(url, box_size=4)
    buffer = io.BytesIO()
    auth_code_image.save(buffer)
    base64_image = base64.b64encode(buffer.getvalue()).decode()
    continue_url = f'{request.host_url}app?state={auth_code_flow["state"]}'
    return '<div style="text-align: center; width: 100%;">' +\
        f'<img src="data:image/png;base64,{base64_image}" alt="Login QR code"></p>' +\
        '<p>请扫码登录您的 Microsoft™ 账号</p>' +\
        f'<p>登陆完成后点击这里<a href="{continue_url}">继续</a>' +\
        f'<br/><p>您的电纸书设备拥有完整版浏览器？请点击<a href="{url}">这里</a></p>'


@app.route("/auth_callback")
def auth():
    state = request.args.get('state', '')
    if state not in temp_token_mappings:
        # Error
        return f'<p>登陆失败</p><p>请<a href="{request.host_url}">重试</a></p>'

    auth_token_flow = temp_token_mappings.pop(state)
    auth_token_reply = request.args.copy()
    res = ms_app.acquire_token_by_auth_code_flow(
        auth_token_flow, auth_token_reply,
        data={"client_secret": CLIENT_SERCERT},
    )
    # Kindle needs to get it later
    temp_res_mappings.update({state: res})

    continue_url = f"{request.host_url}app?state={state}"
    return '<div style="text-align: center; width: 100%;">' +\
        '<p>登录成功</p>' +\
        '<p>请在电纸书设备上点击“继续”</p>' +\
        f'<p>或在当前设备点击<a href="{continue_url}">这里</a></p>'


@app.route("/auth_token")
def auth_token():
    state = request.args.get('state', '')
    if state not in temp_res_mappings:
        # Error
        return jsonify({}), 404, {"Content-Type":"application/json"}

    # Pop: all data will be maintained on the device
    res = temp_res_mappings.pop(state)

    return jsonify(res), 200, {"Content-Type":"application/json"}


@app.route("/auth_refresh")
def auth_refresh():
    res = ms_app.acquire_token_by_refresh_token(
        request.args.get("token", ""),
        scopes=constant.MS_TODO_SCOPE,
        data={"client_secret": CLIENT_SERCERT},
    )
    return f"Refresh auth to get the token: {res}"


@app.route("/app")
def kodos_app():
    # TODO: Make the page
    return f"{request.args.get('state', '')}"


@app.route("/tasks")
def tasks():
    return "Get tasks"


@app.route("/taskfolders")
def taskfolders():
    return "Get folder"
