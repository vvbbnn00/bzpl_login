import configparser
import os
from datetime import datetime

import MySQLdb


def _init():
    global _global_dict
    _global_dict = {}
    global user_token
    user_token = {}
    setting_init()


def setting_init():
    cfg = "./flask_login_panel/settings/mysql.ini"
    conf = configparser.ConfigParser()
    if not os.path.exists(cfg):
        f = open(cfg, 'wb')
        f.close()
    conf.read(cfg)
    if not conf.has_section("Mysql"):
        conf.add_section("Mysql")
    if not conf.has_section("Email"):
        conf.add_section("Email")
    if not conf.has_section("Vaptcha"):
        conf.add_section("Vaptcha")

    if not conf.has_option("Mysql", "Mysql_host"):
        conf.set("Mysql", "Mysql_host", "localhost")
        Mysql_host = "localhost"
    else:
        Mysql_host = conf.get("Mysql", "Mysql_host")
    set_value("Mysql_host", Mysql_host, local=True)

    if not conf.has_option("Mysql", "Mysql_user"):
        conf.set("Mysql", "Mysql_user", "root")
        Mysql_user = "root"
    else:
        Mysql_user = conf.get("Mysql", "Mysql_user")
    set_value("Mysql_user", Mysql_user, local=True)

    if not conf.has_option("Mysql", "Mysql_pass"):
        conf.set("Mysql", "Mysql_pass", "root")
        Mysql_pass = "root"
    else:
        Mysql_pass = conf.get("Mysql", "Mysql_pass")
    set_value("Mysql_pass", Mysql_pass, local=True)

    if not conf.has_option("Mysql", "Mysql_pass"):
        conf.set("Mysql", "Mysql_pass", "root")
        Mysql_pass = "root"
    else:
        Mysql_pass = conf.get("Mysql", "Mysql_pass")
    set_value("Mysql_pass", Mysql_pass, local=True)

    if not conf.has_option("Email", "Email_host"):
        conf.set("Email", "Email_host", "")
        Email_host = ""
    else:
        Email_host = conf.get("Email", "Email_host")
    set_value("Email_host", Email_host, local=True)

    if not conf.has_option("Email", "Email_user"):
        conf.set("Email", "Email_user", "")
        Email_user = ""
    else:
        Email_user = conf.get("Email", "Email_user")
    set_value("Email_user", Email_user, local=True)

    if not conf.has_option("Email", "Email_pass"):
        conf.set("Email", "Email_pass", "")
        Email_pass = ""
    else:
        Email_pass = conf.get("Email", "Email_pass")
    set_value("Email_pass", Email_pass, local=True)

    if not conf.has_option("Email", "Email_port"):
        conf.set("Email", "Email_port", "")
        Email_port = ""
    else:
        Email_port = conf.get("Email", "Email_port")
    set_value("Email_port", Email_port, local=True)

    if not conf.has_option("Vaptcha", "secret_key"):
        conf.set("Vaptcha", "secret_key", "")
        secret_key = ""
    else:
        secret_key = conf.get("Vaptcha", "secret_key")
    set_value("secret_key", secret_key, local=True)
    conf.write(open(cfg, 'w'))
    return 0


def set_value(name, value, change=False, local=False):
    result = None
    if local:
        _global_dict[name] = value
        return
    try:
        db = MySQLdb.connect(_global_dict['Mysql_host'], _global_dict['Mysql_user'], _global_dict['Mysql_pass'], charset='utf8')
        cursor = db.cursor()
        database = "SELECT * FROM db_vsctlr.VSCTLR_SETTINGS WHERE SettingName = '%s'" % (name)
        cursor.execute(database)
        result = cursor.fetchone()
        if result is None:
            database = """REPLACE INTO db_vsctlr.VSCTLR_SETTINGS(SettingName, S_Value)
                         VALUES ('%s', '%s')""" % (name, str(value))
            _global_dict[name] = value
            cursor.execute(database)
        else:
            if not change:
                _global_dict[name] = result[1]
            else:
                database = """REPLACE INTO db_vsctlr.VSCTLR_SETTINGS(SettingName, S_Value)
                             VALUES ('%s', '%s')""" % (name, str(value))
                _global_dict[name] = value
                cursor.execute(database)
        db.close()
    except Exception as e:
        print('发生错误的文件：', e.__traceback__.tb_frame.f_globals['__file__'])
        print('错误所在的行号：', e.__traceback__.tb_lineno)
        print('错误信息', e)
        return -1
    return 0


def get_value(name, def_value=None):
    try:
        return _global_dict[name]
    except KeyError:
        print("错误的查询键值 %s" % name)
        return def_value


def check_token(token):
    try:
        return user_token[token]
    except KeyError:
        return -1


def push_token(token, username):
    user_token[token] = username


def pop_token(token):
    try:
        user_token.pop(token)
    except KeyError:
        return -1