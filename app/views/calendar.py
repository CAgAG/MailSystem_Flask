import datetime

from flask import Blueprint, render_template, \
    request, redirect, url_for, session, jsonify

from app import database

calendar = Blueprint('calendar', __name__)


@calendar.route('/')
def index():
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))

    rets = {
        'calendars': []
    }
    cs = database.get_calendar_by_username(username=username)
    for c in cs:
        ctx = {
            'title': c.title,
            'content': c.content,
            'date': c.target,
            'id': c.id
        }

        rets['calendars'].append(ctx)

    return render_template('calendar.html', **rets)


@calendar.route('/add', methods=["POST"])
def add():
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))

    title = request.form.get('title')
    content = request.form.get('content')
    sdate = request.form.get('date')
    date = datetime.datetime.strptime(sdate, "%Y-%m-%d %H:%M:%S")
    c_id = database.insert_calendar_by_username(username=username,
                                                title=title,
                                                content=content,
                                                date=date)

    word = f"""
    <div class="layui-col-md6" id="card_{ c_id }" style="background: #00b386">
                <div class="layui-card">
                    <div class="layui-card-header">
                        <button class="layui-btn layui-btn-xs layui-btn-radius layui-btn-danger">{c_id}</button>{ title } - { date }

                    </div>
                    <div class="layui-card-body">
                        { content }
                    </div>
                </div>
    </div>
    """

    ctx = {
        'word': word,
        'c_id': c_id
    }
    return jsonify(ctx)


@calendar.route('/delete', methods=["POST"])
def delete():
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))

    id = request.form.get('id')
    code = database.delete_calendar_by_id(id=id)
    if code == 1:
        result = '删除成功'
    else:
        result = '删除失败'
    return result, 200
