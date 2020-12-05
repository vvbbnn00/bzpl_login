"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import *
from flask_login_panel import app
from flask_login_panel.mods import mod_safety
from flask_login_panel.mods import mod_mysql
from flask_login_panel.mods import mod_settings
import requests
import re


@app.route('/login')
def login():
    url_to = request.args.get('url_to', '/get_login_status')
    username = request.cookies.get('user')
    token = request.cookies.get('token')
    u_pattern = "^[a-zA-Z0-9_-]{2,16}$"
    if mod_safety.check_pattern(u_pattern, username):
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
    if not mod_safety.check_pattern(u_pattern, username):
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
        'secretkey': f'{mod_settings.get_value("secret_key")}',
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
    if mod_safety.check_pattern(u_pattern, username):
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


@app.route('/do_reg', methods=['POST'])
def do_reg():
    username = request.form['username']
    ori_passwd = request.form['password']
    passwd = mod_safety.pass_hash(ori_passwd)
    email = request.form['email']
    v_token = request.form['token']
    ip = request.form['ip']
    u_pattern = "^[a-zA-Z0-9_-]{2,16}$"
    p_pattern = "^(?![0-9]+$)(?![a-z]+$)(?![A-Z]+$)(?!([^(0-9a-zA-Z)])+$).{6,20}$"
    e_pattern = "^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$"
    if not mod_safety.check_pattern(u_pattern, username) or not mod_safety.check_pattern(p_pattern, ori_passwd) or not \
            mod_safety.check_pattern(e_pattern, email):
        return {
            'code': 403,
            'msg': "请求不合法！"
        }
    v_data = {
        'id': '5f11cf308d41fe366eb1e82a',
        'secretkey': f'{mod_settings.get_value("secret_key")}',
        'scene': 2,
        'token': v_token,
        'ip': ip
    }
    print(f'[注册尝试] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 来自ip:{ip} 的用户尝试以用户名 {username} 注册 密码hash：'
          f'{passwd} 电子邮箱 {email}。')
    v_response = requests.post("http://0.vaptcha.com/verify", v_data).json()
    if v_response['success'] != 1:
        return {
            'code': 403,
            'msg': '服务器端二次验证失败，这可能是ADBlock或uBlock等去广告插件屏蔽IP检测插件导致的。建议：请在添加该网站为白名单后重试。'
        }
    result = mod_mysql.create_user(username=username, pass_hash=passwd, email=email)
    if result['code'] == 0:
        return {
            'code': 200,
            'msg': "success."
        }
    else:
        return {
            'code': 403,
            'msg': result['msg']
        }


@app.route('/activate')
def do_active():
    token_id = request.args.get('token_id', "")
    token = request.args.get('token', "")
    if token == "" or token_id == "":
        return render_template("activate.html",
                               success="display:none",
                               failed="",
                               fail_msg="请求不合法！",
                               enable_url="//",
                               title='账户激活',
                               year=datetime.now().year,
                               )
    result = mod_mysql.verify_link(token_id, token)
    if result['code'] == 0:
        return render_template("activate.html",
                               success="",
                               failed="display:none",
                               enable_url="",
                               url_to="/login",
                               title='账户激活',
                               year=datetime.now().year,
                               )
    else:
        return render_template("activate.html",
                               success="display:none",
                               failed="",
                               fail_msg=result['msg'],
                               enable_url="//",
                               title='账户激活',
                               year=datetime.now().year,
                               )
