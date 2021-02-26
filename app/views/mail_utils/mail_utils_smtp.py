import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

"""
code=1: 成功发送,
    =0: 失败
"""
def send_mail_by_smtp(user_addr: str, pwd: str, SSL: str, port: int,
                      receiver: list,
                      From: str, To: str, title: str, content: str, files: list):
    user_id = user_addr
    user_pwd = pwd
    receiver = receiver

    # 1. 连接邮箱服务器
    con = smtplib.SMTP_SSL(SSL, port)

    # 2. 登录邮箱
    con.login(user_id, user_pwd)

    # 2. 准备数据
    # 创建邮件对象
    msg = MIMEMultipart()

    # 设置邮件主题
    subject = Header(title, 'utf-8')
    msg['Subject'] = subject

    # 设置邮件发送者
    if user_addr not in From:
        From += f' <{user_addr}>'
    msg['From'] = From

    # 设置邮件接受者
    msg['To'] = To

    # 添加文字内容
    # text = MIMEText('from python', 'plain', 'utf-8')
    text = MIMEText(content, 'html', 'utf-8')
    msg.attach(text)

    for file in files:
        # 构造附件
        with open(file, "rb") as data:
            att = MIMEText(data.read(), "base64", "utf-8")
        att["Content-Type"] = "application/octet-stream"
        # 附件名称为中文时的写法
        att.add_header("Content-Disposition",
                       "attachment",
                       filename=("gbk", "", file.split('/')[-1]))
        msg.attach(att)

    code = 1
    try:
        # 3.发送邮件
        con.sendmail(user_id, receiver, msg.as_string())
    except Exception:
        code = 0
    finally:
        con.quit()
    return code


def default_163_send_by_smtp():
    pass
