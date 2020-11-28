"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import *
from flask_login_panel import app
from flask_login_panel.mods import mod_safety
from flask_login_panel.mods import mod_mysql
import requests
import re


@app.route('/login')
def login():
    url_to = request.args.get('url_to', '/get_login_status')
    username = request.cookies.get('user')
    token = request.cookies.get('token')
    u_pattern = "^[a-zA-Z0-9_-]{2,16}$"
    if username is None:
        username_check = False
    else:
        if len(username) in range(2, 17):
            username_check = ('' if re.search(u_pattern, username) is None else re.search(u_pattern, username)
                              .group()) == username
        else:
            username_check = False
    if username_check:
        result = mod_mysql.check_token(username, token)
    else:
        result = -1
    if result == 0:
        return redirect(url_to)
    return render_template(
        'login.html',
        title='登录',
        year=datetime.now().year,
        url_to=url_to,
    )


@app.route('/get_login_status')
def login_status():
    username = request.cookies.get('user')
    token = request.cookies.get('token')
    if mod_mysql.check_token(username, token) == 0:
        return {
            'code': 0,
            'user': username,
            'token': token,
        }
    else:
        return {
            'code': -1,
            'msg': "用户名或密码错误"
        }


@app.route('/do_login', methods=['POST'])
def check_user():
    username = request.form['username']
    u_pattern = "^[a-zA-Z0-9_-]{2,16}$"
    if len(username) in range(2, 17):
        username_check = ('' if re.search(u_pattern, username) is None else re.search(u_pattern, username)
                          .group()) == username
    else:
        username_check = False
    if not username_check:
        return {
            'code': 403,
            'msg': '用户名请求不合法！'
        }
    password = request.form['password']
    password = mod_safety.pass_hash(password)
    v_token = request.form['token']
    remember_me = request.form['remember_me']
    ip = request.form['ip']
    v_data = {
        'id': '5f11cf308d41fe366eb1e82a',
        'secretkey': '99f01c002fbf433494a6e2b74a52c8e3',
        'scene': 1,
        'token': v_token,
        'ip': ip
    }
    print(f'[登录尝试] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 来自ip:{ip} 的用户尝试以用户名 {username} 登录 记住我选项：'
          f'{remember_me}。')
    v_response = requests.post("http://0.vaptcha.com/verify", v_data).json()
    if v_response['success'] != 1:
        return {
            'code': 403,
            'msg': '服务器端二次验证失败，这可能是ADBlock或uBlock等去广告插件屏蔽IP检测插件导致的。建议：请在添加该网站为白名单后重试。'
        }
    result = mod_mysql.check_user(username, password, ip)
    if result['code'] != 0:
        return {
            'code': result['code'],
            'msg': result['msg']
        }
    else:
        token = "Login:" + username + "PPpp" + password
        token = mod_safety.pass_hash(token)
        # 跨站处理尚未完成
        result = Response(json.dumps({
            "code": 200,
        }), content_type='application/json')
        if remember_me == "true":
            result.set_cookie('user', username, domain=".vvbbnn00.cn", max_age=604800)
            result.set_cookie('token', token, domain=".vvbbnn00.cn", max_age=604800)
        else:
            result.set_cookie('user', username, domain=".vvbbnn00.cn")
            result.set_cookie('token', token, domain=".vvbbnn00.cn")
        return result


@app.route('/logout')
def logout():
    url_to = request.args.get('url_to', '/login')
    url_to = escape(url_to)
    response_data = Response(render_template(
        'logout.html',
        title='登出',
        year=datetime.now().year,
        url_to=url_to,
    ))
    response_data.delete_cookie("user", domain=".vvbbnn00.cn")
    response_data.delete_cookie("token", domain=".vvbbnn00.cn")
    return response_data


@app.route('/register')
def register():
    url_to = request.args.get('url_to', '/get_login_status')
    username = request.cookies.get('user')
    token = request.cookies.get('token')
    u_pattern = "^[a-zA-Z0-9_-]{2,16}$"
    if username is None:
        username_check = False
    else:
        if len(username) in range(2, 17):
            username_check = ('' if re.search(u_pattern, username) is None else re.search(u_pattern, username)
                              .group()) == username
        else:
            username_check = False
    if username_check:
        result = mod_mysql.check_token(username, token)
    else:
        result = -1
    if result == 0:
        return redirect(url_to)
    return render_template(
        'register.html',
        title='注册',
        year=datetime.now().year,
        url_to=url_to,
    )


@app.route('/test/sendmail')
def test_send_mail():
    return mod_mysql.create_verify_link("test", "1", "vvbbnn00@foxmail.com")
