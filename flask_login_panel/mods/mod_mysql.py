import traceback

from flask_login_panel.mods import mod_safety
from flask_login_panel.mods.mod_settings import *
import datetime
import redis
from flask_login_panel.mods import mod_email

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
Mysql_host = get_value("Mysql_host")
Mysql_pass = get_value("Mysql_pass")
Mysql_user = get_value("Mysql_user")

temporary_token_list = {}


def check_user(username, password, ip):
    # 判断用户名密码是否正确
    try:
        r = redis.Redis(connection_pool=pool)
        r_p = r.get("passwd_" + username)
        uid = r.get("uid_" + username)
        if (r_p is not None) and (uid is not None):
            passwd = r_p
        else:
            db = MySQLdb.connect(Mysql_host, Mysql_user, Mysql_pass, charset='utf8')
            cursor = db.cursor()
            sql = "SELECT * FROM db_user.user_up WHERE USERNAME = '%s'" % username
            cursor.execute(sql)
            result = cursor.fetchone()
            uid = result[0]
            passwd = result[2]
            r.set('passwd_' + username, passwd, ex=3600)
            r.set('uid_' + username, uid, ex=3600)
            db.close()
        if password == passwd:
            v_token = "Login:" + username + "PPpp" + passwd
            v_token = mod_safety.pass_hash(v_token)
            r.set('token_' + username, v_token, ex=3600)
            db = MySQLdb.connect(Mysql_host, Mysql_user, Mysql_pass, charset='utf8')
            cursor = db.cursor()
            sql = f"SELECT * FROM db_user.user_detail WHERE UID = '{uid}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None or result[5] == -1:
                return {
                    'code': 2,
                    'msg': "您被禁止登录本网站，请联系网站管理员！"
                }
            if result[5] == 2:
                return {
                    'code': 2,
                    'msg': "请先在邮件中激活该账户！"
                }
            login_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = f"REPLACE INTO db_user.user_detail (`uid`, `Last_Login`, `Login_IP`) VALUES ('{uid}', " \
                  f"'{login_dt}', '{ip}')"
            cursor.execute(sql)

            return {
                'code': 0,
                'UID': uid
            }
        else:
            return {
                'code': 1,
                'msg': '用户名或密码错误！'
            }
    except Exception as e:
        print('发生错误的文件：', e.__traceback__.tb_frame.f_globals['__file__'])
        print('错误所在的行号：', e.__traceback__.tb_lineno)
        print('错误信息', e)
        return {
            'code': -1,
            'msg': '未知错误，请联系网站管理员！'
        }


def check_token(username, token):
    try:
        r = redis.Redis(connection_pool=pool)
        r_p = r.get("token_" + username)
        if r_p is not None:
            v_token = r_p
        else:
            db = MySQLdb.connect(Mysql_host, Mysql_user, Mysql_pass, charset='utf8')
            cursor = db.cursor()
            sql = "SELECT * FROM db_user.user_up WHERE USERNAME = '%s'" % username
            cursor.execute(sql)
            result = cursor.fetchone()
            passwd = result[2]
            db.close()
            v_token = "Login:" + username + "PPpp" + passwd
            v_token = mod_safety.pass_hash(v_token)
            r.set('token_' + username, v_token, ex=3600)
        if token == v_token:
            return 0
        else:
            return -1
    except Exception as e:
        print('发生错误的文件：', e.__traceback__.tb_frame.f_globals['__file__'])
        print('错误所在的行号：', e.__traceback__.tb_lineno)
        print('错误信息', e)
        return -1


def create_verify_link(username, uid, email):
    try:
        db = MySQLdb.connect(Mysql_host, Mysql_user, Mysql_pass, charset='utf8')
        cursor = db.cursor()
        sql = f"SELECT * FROM db_user.user_detail WHERE UID = '{uid}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if result is None:
            return {
                'code': 1,
                'msg': "非法请求！"
            }
        if result[5] != 2:
            return {
                'code': 1,
                'msg': "非法请求！"
            }
        token_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S_" + uid + mod_safety.random_number_code(10))
        token = mod_safety.pass_hash(mod_safety.random_secret_key(32))
        r = redis.Redis(connection_pool=pool)
        r.set("v_code_" + token_id, token, ex=3600)
        r.set("v_uid_" + token_id, token, ex=3600)
        mod_email.send_verify_message(username, email, token_id, token)
        return {
            'code': 0,
            'msg': '注册成功，一封激活邮件已发送至您的邮箱，为避免重复注册，请在一小时内激活！'
        }
    except Exception as e:
        print('发生错误的文件：', e.__traceback__.tb_frame.f_globals['__file__'])
        print('错误所在的行号：', e.__traceback__.tb_lineno)
        print('错误信息', e)
        return {
            'code': -1,
            'msg': "未知错误，请联系管理员！"
        }


def verify_link(token_id, token):
    try:
        r = redis.Redis(connection_pool=pool)
        check_code = r.get("v_code_" + token_id) == token_id
        uid = r.set("v_uid_" + token_id, token)
        if check_code is False or uid is None:
            return {
                'code': 1,
                'msg': '该链接已经过期或已被使用，请尝试登录或重新注册！'
            }
        r.delete("v_code_" + token_id)
        r.delete("v_uid_" + token_id)
        db = MySQLdb.connect(Mysql_host, Mysql_user, Mysql_pass, charset='utf8')
        cursor = db.cursor()
        sql = f"REPLACE INTO db_user.user_detail (`uid`, `Status`) VALUES ('{uid}', '{0}')"
        cursor.execute(sql)
        return {
            'code': 0,
            'msg': '账户激活成功，请重新登录！'
        }
    except Exception as e:
        print('发生错误的文件：', e.__traceback__.tb_frame.f_globals['__file__'])
        print('错误所在的行号：', e.__traceback__.tb_lineno)
        print('错误信息', e)
        return {
            'code': -1,
            'msg': "未知错误，请联系管理员！"
        }