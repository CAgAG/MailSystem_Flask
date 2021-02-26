import pymysql
from flask import Flask, render_template, send_file
from flask_sqlalchemy import SQLAlchemy

pymysql.install_as_MySQLdb()

app = Flask(__name__)  # type: Flask
app.config.from_object('config')
# 实例化一个数据库对象
db = SQLAlchemy(app)

from . import models, blueprint_register

db.create_all()

@app.route('/')
def first_page():
    return render_template('login.html')

@app.route('/show/<path:p>', methods=["POST", "GET"])
def show(p: str):
    path = p.replace('..', '')
    return send_file(f'media/{path}')

