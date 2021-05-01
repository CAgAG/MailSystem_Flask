import datetime

from app import db, models


def check_login(username: str, password: str):
    """
    :param username: 用户名
    :param password: 密码
    :return: 提示
    """
    users = models.User.query.filter_by(username=username).all()
    isinstance(users, list)
    if len(users) == 0:
        return '用户不存在'
    user = users[0]
    isinstance(user, models.User)
    pwd = user.password

    if password != pwd:
        return '密码错误'

    return '登录成功'


def check_register(mailName: str, username: str, pwd: str):
    """
    :param mailName: 邮箱
    :param username: 用户名
    :param pwd: 密码
    :return: 提示
    """
    users = models.User.query.filter_by(username=username).all()
    if len(users) != 0:
        return '用户名已存在'

    user = models.User()
    user.username = username
    user.password = pwd
    user.email = mailName
    db.session.add(user)
    db.session.commit()

    return "注册成功"


def get_user_info(username: str) -> models.User:
    """
    :param username: 用户名
    :return: User类
    """
    users = models.User.query.filter_by(username=username).all()
    if len(users) == 0:
        return None
    return users[0]

def reset_user_pwd(username: str) -> int:
    """
    :param username: 用户名
    :return: 结果代码: 1: 成功, 0: 失败
    """
    return update_user_info(username=username, args={
        'password': '12345678'
    })


def insert_mail_account_by_username(username: str, addr: str, SSL: str, pwd: str, port=465):
    """
    :param username: 用户名
    :param addr: 邮箱地址
    :param SSL: SSL服务器
    :param pwd: 密码
    :param port: 端口
    :return: 1: 成功, 0: 失败
    """
    mailaccount = models.MailAccount()
    mailaccount.username = username
    mailaccount.addr = addr
    mailaccount.pwd = pwd
    mailaccount.SSL = SSL
    mailaccount.port = port
    try:
        db.session.add(mailaccount)
        db.session.commit()
    except Exception:
        return 0

    return 1


def get_mail_account_by_username(username: str) -> models.MailAccount:
    """
    :param username: 用户名
    :return: None: 未找到
    """
    MailAccount = models.MailAccount
    try:
        account = MailAccount.query.filter_by(username=username).first()
    except Exception:
        return None
    return account


def insert_mail_by_username(username: str, addr: str, receiver: list,
                            title: str, content: str, From: str, To: str, file=None):
    if file is None:
        file = []
    mail = models.Mail()
    mail.username = username
    mail.addr = addr
    mail.receivers = ";".join(receiver)
    mail.title = title
    mail.content = content
    mail.From = From
    mail.To = To
    if len(file) != 0:
        mail.file = ','.join(file)
    try:
        db.session.add(mail)
        db.session.commit()
        mailtype = models.MailType()
        mailtype.mailid = mail.id
        if len(receiver) > 1:
            mailtype.is_group = True

        db.session.add(mailtype)
        db.session.commit()
    except Exception:
        return -1

    return mail.id


def insert_simple_mail_by_username(username: str, receiver: list,
                                   title: str, content: str, To: str):
    mail = models.Mail()
    mail.username = username
    mail.receivers = ";".join(receiver)
    mail.title = title
    mail.content = content
    mail.To = To
    try:
        db.session.add(mail)
        db.session.commit()
        mailtype = models.MailType()
        mailtype.mailid = mail.id
        if len(receiver) > 1:
            mailtype.is_group = True
        db.session.add(mailtype)
        db.session.commit()
    except Exception:
        return -1

    return mail.id


def update_mail_type(mailid: int, args: dict) -> int:
    mailtype = models.MailType()
    try:
        mailtype.query.filter_by(mailid=mailid).update(args)
        db.session.commit()
    except Exception:
        return 0
    return 1


def get_mail_deleted(mailid: int) -> bool:
    mailtype = models.MailType()
    d = mailtype.query.filter_by(mailid=mailid).first()
    if d is None:
        return None
    return d.is_deleted


def get_mail_star(mailid: int) -> bool:
    mailtype = models.MailType()
    star = mailtype.query.filter_by(mailid=mailid).first()
    if star is None:
        return None
    return star.is_star


def insert_receive_mail_by_username(username: str, addr: str, receiver: list,
                                    title: str, content: str, From: str, To: str, uid: str, file=None):
    if file is None:
        file = []
    mail = models.Mail()
    mailtype = models.MailType()

    user_mails = mail.query.filter_by(username=username).all()
    for m in user_mails:
        user_mail_type = mailtype.query.filter_by(mailid=m.id).first()
        if (user_mail_type is not None) and (user_mail_type.uid == uid):
            return user_mail_type.mailid

    mail.username = username
    mail.addr = addr
    mail.receivers = ";".join(receiver)
    mail.title = title
    mail.content = content
    mail.From = From
    mail.To = To
    if len(file) != 0:
        mail.file = ','.join(file)
    try:
        db.session.add(mail)
        db.session.commit()
        mailtype.mailid = mail.id
        if len(receiver) > 1:
            mailtype.is_group = True
        mailtype.is_received = True
        mailtype.uid = uid
        db.session.add(mailtype)
        db.session.commit()
    except Exception:
        return -1

    return mail.id


def delete_mail_by_id(mailid: int):
    mail_type = models.MailType()
    mail = models.Mail()

    mt = mail_type.query.filter_by(mailid=mailid).first()
    m = mail.query.filter_by(id=mailid).first()

    try:
        db.session.delete(mt)
        db.session.commit()
        db.session.delete(m)
        db.session.commit()
    except Exception:
        return 0
    return 1


def get_draft_mails(username: str):
    mail_type = models.MailType()
    mail = models.Mail()

    rets = {}
    usermails = mail.query.filter_by(username=username).all()
    rets['mails'] = []
    count = 0
    for ma in usermails:
        mt = mail_type.query.filter_by(mailid=ma.id).first()
        flag = mt.is_draft
        flag2 = mt.is_deleted
        if flag and not flag2:
            count += 1
            ret2 = {}
            ret2['from'] = ma.To
            print('draft box from: ==>', ret2['from'])
            ret2['to'] = ma.To
            ret2['receivers'] = ma.receivers
            ret2['date'] = str(ma.updated)
            ret2['title'] = ma.title
            ret2['index'] = 0
            ret2['uid'] = '../sending'
            ret2['content'] = ma.content
            ret2['files'] = []
            ret2['filenames'] = []
            ret2['is_star'] = mt.is_star
            ret2['mail_id'] = mt.mailid

            rets['mails'].append(ret2)
    rets['mail_length'] = count
    return rets


def get_sended_mails(username: str):
    mail_type = models.MailType()
    mail = models.Mail()

    rets = {}
    usermails = mail.query.filter_by(username=username).all()
    rets['mails'] = []
    count = 0
    for ma in usermails:
        mt = mail_type.query.filter_by(mailid=ma.id).first()
        flag = mt.is_sended
        flag2 = mt.is_deleted
        if flag and not flag2:
            count += 1
            ret2 = {}
            ret2['from'] = ma.To
            ret2['to'] = ma.To
            ret2['date'] = str(ma.updated)
            ret2['title'] = ma.title
            ret2['index'] = 0
            ret2['receivers'] = ma.receivers
            ret2['uid'] = '../sending'
            ret2['content'] = ma.content
            ret2['files'] = []
            ret2['filenames'] = []
            ret2['is_star'] = mt.is_star
            ret2['mail_id'] = mt.mailid

            rets['mails'].append(ret2)
    rets['mail_length'] = count
    return rets


def get_deleted_mails(username: str):
    mail_type = models.MailType()
    mail = models.Mail()

    rets = {}
    usermails = mail.query.filter_by(username=username).all()
    rets['mails'] = []
    count = 0
    for ma in usermails:
        mt = mail_type.query.filter_by(mailid=ma.id).first()
        flag = mt.is_deleted
        if flag:
            count += 1
            ret2 = {}
            ret2['from'] = ma.To
            ret2['to'] = ma.To
            ret2['date'] = str(ma.updated)
            ret2['title'] = ma.title
            ret2['index'] = 0
            ret2['receivers'] = ma.receivers
            ret2['uid'] = '../sending'
            ret2['content'] = ma.content
            ret2['files'] = []
            ret2['filenames'] = []
            ret2['is_star'] = mt.is_star
            ret2['mail_id'] = mt.mailid

            rets['mails'].append(ret2)
    rets['mail_length'] = count
    return rets


def get_star_mails(username: str):
    mail_type = models.MailType()
    mail = models.Mail()

    rets = {}
    usermails = mail.query.filter_by(username=username).all()
    rets['mails'] = []
    count = 0
    for ma in usermails:
        mt = mail_type.query.filter_by(mailid=ma.id).first()
        flag = mt.is_star
        flag2 = mt.is_deleted
        if flag and not flag2:
            count += 1
            ret2 = {}
            ret2['from'] = ma.To
            print('draft box from: ==>', ret2['from'])
            ret2['to'] = ma.To
            ret2['receivers'] = ma.receivers
            ret2['date'] = str(ma.updated)
            ret2['title'] = ma.title
            ret2['index'] = 0
            ret2['uid'] = '../sending'
            ret2['content'] = ma.content
            ret2['files'] = []
            ret2['filenames'] = []
            ret2['is_star'] = mt.is_star
            ret2['mail_id'] = mt.mailid

            rets['mails'].append(ret2)
    rets['mail_length'] = count
    return rets


def get_group_mails(username: str):
    mail_type = models.MailType()
    mail = models.Mail()

    rets = {}
    usermails = mail.query.filter_by(username=username).all()
    rets['mails'] = []
    count = 0
    for ma in usermails:
        mt = mail_type.query.filter_by(mailid=ma.id).first()
        flag = mt.is_group
        flag2 = mt.is_deleted
        if flag and not flag2:
            count += 1
            ret2 = {}
            ret2['from'] = ma.To
            print('draft box from: ==>', ret2['from'])
            ret2['to'] = ma.To
            ret2['receivers'] = ma.receivers
            ret2['date'] = str(ma.updated)
            ret2['title'] = ma.title
            ret2['index'] = 0
            ret2['uid'] = '../sending'
            ret2['content'] = ma.content
            ret2['files'] = []
            ret2['filenames'] = []
            ret2['is_star'] = mt.is_star
            ret2['mail_id'] = mt.mailid

            rets['mails'].append(ret2)
    rets['mail_length'] = count
    return rets


def insert_calendar_by_username(username: str, title: str, content: str, date):
    """
    :param username: 用户名
    :param title: 标题
    :param content: 内容
    :param date: 日期
    :return: 日期数据库id
    """
    calendar = models.Calendar()

    calendar.username = username
    calendar.title = title
    calendar.content = content
    calendar.target = date
    db.session.add(calendar)
    db.session.commit()

    return calendar.id


def delete_calendar_by_id(id: str):
    """
    :param id: 删除id
    :return:
    """
    calendar = models.Calendar()

    ca = calendar.query.filter_by(id=int(id)).first()

    try:
        db.session.delete(ca)
        db.session.commit()
    except Exception:
        return 0

    return 1


def get_calendar_by_username(username: str):
    calendar = models.Calendar()
    ca = calendar.query.filter_by(username=username).all()
    return ca

def update_user_info(username: str, args: dict):
    usrs = models.User()
    try:
        usrs.query.filter_by(username=username).update(args)
        db.session.commit()
    except Exception:
        return 0
    return 1

def get_mail_content_by_id(mailid: int):
    mail = models.Mail()

    m = mail.query.filter_by(id=mailid).first()
    content = m.content

    return content if content is not None else ''

def get_mail_title_by_id(mailid: int):
    mail = models.Mail()

    m = mail.query.filter_by(id=mailid).first()
    content = m.title

    return content if content is not None else ''

def get_mail_receivers_by_id(mailid: int):
    mail = models.Mail()

    m = mail.query.filter_by(id=mailid).first()
    content = m.receivers

    return content if content is not None else ''
