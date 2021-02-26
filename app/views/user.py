import datetime

from flask import Blueprint, render_template, \
    request, redirect, url_for, session

from app import database

user = Blueprint('user', __name__)


@user.route('/index', methods=['POST', 'GET'])
def index():
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.login'))

    mUser = database.get_user_info(username)
    cs = database.get_calendar_by_username(username=username)

    td = datetime.datetime.now()

    rets = {}
    rets['calendars'] = []
    for c in cs:
        ct = c.target
        diff = ct - td
        if abs(diff.days) <= 1:
            ctx = {
                'title': c.title,
            }
            rets['calendars'].append(ctx)

    rets['username'] = mUser.username
    rets['email'] = mUser.email
    rets['fridends'] = mUser.friend
    rets['today'] = td.strftime('%Y-%m-%d')
    rets['mlen'] = len(rets['calendars'])

    return render_template('index.html', **rets)


@user.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    result = database.check_login(username, password)

    if result == '登录成功':
        session['username'] = username
        return redirect(url_for('user.index'))
    else:
        ctx = {
            'results': result
        }
        return render_template('login.html', **ctx)


@user.route('/register', methods=['POST'])
def register():
    mailName = request.form.get('rmailname')

    username = request.form.get('rusername')
    password = request.form.get('rpassword')

    result = database.check_register(mailName, username, password)
    ctx = {
        'results2': result
    }
    return render_template('login.html', **ctx)


@user.route('/editpage')
def editpage():
    return render_template('user_info.html')


@user.route('/edit', methods=['POST'])
def edit():
    username = session.get('username')

    addr = request.form.get('addr')
    code = 0
    if addr != ' ':
        code += database.update_user_info(username=username,
                                  args={
                                      'email': addr,
                                  })
    pwd = request.form.get('password')
    if pwd != ' ':
        code += database.update_user_info(username=username,
                                  args={
                                      'password': pwd
                                  })

    flag = code == 2
    ctx = {
        'title': '修改结果',
        'content': '修改成功'if flag else '修改失败'
    }

    return render_template('show_result.html', **ctx)
