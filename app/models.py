from datetime import datetime

from app import db


class User(db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String(80), primary_key=True)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    friend = db.Column(db.Text, nullable=True, default='')

    def __repr__(self):
        return f'user: {self.username}'


class MailAccount(db.Model):
    __tablename__ = 'mailaccount'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    addr = db.Column(db.String(80), nullable=False)
    SSL = db.Column(db.String(80), default='smtp.163.com')
    pwd = db.Column(db.String(80), default='HSJKBVWZUUKPOOOK')
    port = db.Column(db.Integer, default=465)

    last_received = db.Column(db.DateTime, default=datetime.now())

    username = db.Column(db.String(80), db.ForeignKey('user.username'))

    def __repr__(self):
        return f'mailaccount: {self.addr}'


class Mail(db.Model):
    __tablename__ = 'mail'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    addr = db.Column(db.String(80), nullable=True)
    receivers = db.Column(db.Text, nullable=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=True)
    From = db.Column(db.Text, nullable=True)
    To = db.Column(db.Text, nullable=False)
    file = db.Column(db.Text, nullable=True)

    crated = db.Column(db.DateTime, default=datetime.now)
    updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    username = db.Column(db.String(80), db.ForeignKey('user.username'))

    def __repr__(self):
        return f'mail: {self.id}-{self.title}-{self.username}'


class MailType(db.Model):
    __tablename__ = 'mailtype'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_star = db.Column(db.Boolean, nullable=True, default=False)
    is_group = db.Column(db.Boolean, nullable=True, default=False)
    is_draft = db.Column(db.Boolean, nullable=True, default=False)
    is_sended = db.Column(db.Boolean, nullable=True, default=False)
    is_deleted = db.Column(db.Boolean, nullable=True, default=False)

    is_received = db.Column(db.Boolean, nullable=True, default=False)
    uid = db.Column(db.String(80), nullable=True, default='#')

    mailid = db.Column(db.Integer, db.ForeignKey('mail.id'))

    def __repr__(self):
        return f'mailtype: {self.id}->{self.mailid}'


class Calendar(db.Model):
    __tablename__ = 'calendar'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)

    crated = db.Column(db.DateTime, default=datetime.now)
    updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    target = db.Column(db.DateTime, default=datetime.now)

    username = db.Column(db.String(80), db.ForeignKey('user.username'))

