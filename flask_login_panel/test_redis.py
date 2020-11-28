import redis

try:
    pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
except Exception as e:
    print("Redis服务器连接失败！")

if __name__ == '__main__':
    try:
        r = redis.Redis(connection_pool=pool)
        r.set('food', 'mutton', ex=3600)  # key是"food" value是"mutton" 将键值对存入redis缓存
        print(r.get('food'))  # mutton 取出键food对应的值
        print(r.get('username'))  # mutton 取出键food对应的值
    except Exception as e:
        print('发生错误的文件：', e.__traceback__.tb_frame.f_globals['__file__'])
        print('错误所在的行号：', e.__traceback__.tb_lineno)
        print('错误信息', e)
        print("Redis服务器连接失败！")

