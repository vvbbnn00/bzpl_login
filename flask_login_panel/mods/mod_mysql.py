import traceback

from flask_login_panel.mods import mod_safety
from flask_login_panel.mods.mod_settings import *
import redis

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
Mysql_host = get_value("Mysql_host")
Mysql_pass = get_value("Mysql_pass")
user_Mysql_db = "db_user"
Mysql_user = get_value("Mysql_user")
Mysql_db = get_value("Mysql_db")

temporary_token_list = {}


def check_user(username, password):
    # 判断用户名密码是否正确
    try:
        r = redis.Redis(connection_pool=pool)
        r_p = r.get("passwd_" + username)
        if r_p is not None:
            passwd = r_p
        else:
            db = MySQLdb.connect(Mysql_host, Mysql_user, Mysql_pass, user_Mysql_db, charset='utf8')
            cursor = db.cursor()
            sql = "SELECT * FROM user_up WHERE USERNAME = '%s'" % username
            cursor.execute(sql)
            result = cursor.fetchone()
            passwd = result[2]
            r.set('passwd_'+username, passwd, ex=3600)
            db.close()
        if password == passwd:
            db = MySQLdb.connect(Mysql_host, Mysql_user, Mysql_pass, Mysql_db, charset='utf8')
            cursor = db.cursor()
            sql = "SELECT * FROM vsctlr_user WHERE USERNAME = '%s'" % username
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                sql = "INSERT INTO vsctlr_user(username,authority) values('%s','%s')" % (username, "0")
                print(sql)
                cursor.execute(sql)
                db.close()
                return {"authority": "0"}
            db.close()
            return {"authority": result[1]}
        else:
            return -1
    except Exception as e:
        return -1


def get_sql_status():
    try:
        start_time = datetime.now()
        db = MySQLdb.connect(Mysql_host, Mysql_user, Mysql_pass, Mysql_db, charset='utf8')
        end_time = datetime.now()
        time = end_time - start_time
        cursor = db.cursor()
        sql = f"SELECT * FROM vsctlr_software"
        cursor.execute(sql)
        result = cursor.fetchall()
        app_sum = len(result)
        return {
            'status': f'正常（响应时间{time.microseconds}ms）',
            'software': app_sum
        }
    except Exception as e:
        return {
            'status': f'异常',
            'software': 'Null'
        }


def check_token(username, token):
    try:
        start_time = datetime.now()
        r = redis.Redis(connection_pool=pool)
        r_p = r.get("token_" + username)
        if r_p is not None:
            v_token = r_p
        else:
            db = MySQLdb.connect(Mysql_host, Mysql_user, Mysql_pass, user_Mysql_db, charset='utf8')
            cursor = db.cursor()
            sql = "SELECT * FROM user_up WHERE USERNAME = '%s'" % username
            cursor.execute(sql)
            result = cursor.fetchone()
            passwd = result[2]
            db.close()
            v_token = "Login:" + username + "PPpp" + passwd
            v_token = mod_safety.pass_hash(v_token)
            r.set('token_' + username, v_token, ex=3600)
        end_time = datetime.now()
        time = end_time - start_time
        print(f'响应时间{time.microseconds/1000}ms')
        if token == v_token:
            return 0
        else:
            return -1
    except Exception as e:
        return -1

