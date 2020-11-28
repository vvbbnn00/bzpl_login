import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from flask_login_panel.mods import mod_settings

sender = mod_settings.get_value('Email_user')
host = mod_settings.get_value('Email_host')
passwd = mod_settings.get_value('Email_pass')
port = mod_settings.get_value('Email_port')


def send_verify_message(username, email, token_id, token):
    receivers = [email]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    html = f"""尊敬的{username}：<br>
您好！<br>
感谢您注册<a href="https://www.vvbbnn00.cn" title="不做评论">不做评论</a>，请在一小时内点击以下链接激活您的账户：<br>
<a href="https://login.vvbbnn00.cn/activate?token_id={token_id}&token={token}" title="点击此处以激活您的账户">验证链接</a><br>
如果您无法点击链接，请将以下地址复制到浏览器的导航栏中：<br>
https://login.vvbbnn00.cn/activate?token_id={token_id}&token={token}<br>
如果您没有进行过注册，则请忽视该邮件。<br>
最后，祝您身体健康，再见！<br>
<br><br>
不做评论
"""
    message = MIMEText(html, 'html', 'utf-8')
    message['From'] = formataddr(('不做评论官方账号', sender))  # 发送者
    message['To'] = Header(f"{email}", 'utf-8')  # 接收者

    subject = '激活您的账号'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtp_obj = smtplib.SMTP_SSL(host)
        smtp_obj.connect(host, port)
        smtp_obj.login(sender, passwd)
        smtp_obj.sendmail(sender, receivers, message.as_string())
        return 0
    except smtplib.SMTPException as e:
        print('发生错误的文件：', e.__traceback__.tb_frame.f_globals['__file__'])
        print('错误所在的行号：', e.__traceback__.tb_lineno)
        print('错误信息', e)
        return -1

