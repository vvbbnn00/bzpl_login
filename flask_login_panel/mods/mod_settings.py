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
    mysql_cfg = "./flask_login_panel/settings/mysql.ini"
    conf = configparser.ConfigParser()
    if not os.path.exists(mysql_cfg):
        f = open(mysql_cfg, 'wb')
        f.close()
    conf.read(mysql_cfg)
    if not conf.has_section("Mysql"):
        conf.add_section("Mysql")

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
    if not conf.has_option("Mysql", "Mysql_db"):
        conf.set("Mysql", "Mysql_db", "db_vsctlr")
        Mysql_db = "db_vsctlr"
    else:
        Mysql_db = conf.get("Mysql", "Mysql_db")
    set_value("Mysql_db", Mysql_db, local=True)
    conf.write(open(mysql_cfg, 'w'))

    result = 0
    result += set_value("Temp_Dir", "temp/")  # 临时文件目录（建议相对路径）
    result += set_value("Log_Dir", "log/")  # 日志文件目录
    result += set_value("db_connected", "false")  # 检验数据库是否连接成功
    if result != 0:
        print("错误！请检查您的mysql是否配置正确！")
        return -1
    return 0


def set_value(name, value, change=False, local=False):
    result = None
    if local:
        _global_dict[name] = value
        return
    try:
        db = MySQLdb.connect(_global_dict['Mysql_host'], _global_dict['Mysql_user'], _global_dict['Mysql_pass'],
                             _global_dict['Mysql_db'], charset='utf8')
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