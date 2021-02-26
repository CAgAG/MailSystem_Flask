import datetime, os, shutil, copy

from flask import Blueprint, render_template, \
    request, redirect, url_for, session, jsonify

from app import database

from app.views import mail_utils

mail_app = Blueprint('mail', __name__)


def default_title():
    return f''


def get_server_pop_or_imap():
    spi = session.get('pi', 'pop')
    return spi


def generate_To_sendto(send_to: str):
    send_to = send_to.split(';')

    if len(send_to) >= 2:
        To = f'{len(send_to)} users'
    else:
        To = ','.join(send_to)

    return To, send_to


@mail_app.route('/welcome')
def welcome():
    ss = get_server_pop_or_imap()
    ctx = {
        'ss': ss
    }
    return render_template('welcome.html', **ctx)


@mail_app.route('/change_server', methods=["POST"])
def change_server():
    server = request.form.get("server")
    session['pi'] = str(server)
    return '协议切换成功', 200


@mail_app.route('/up_account', methods=["POST", "GET"])
def up_account():
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))

    if request.method == "POST":
        addr = request.form.get("addr")
        SSL = request.form.get("SSL")
        if 'smtp' not in SSL:
            SSL = 'smtp.' + SSL
        pwd = request.form.get("password")

        result = database.insert_mail_account_by_username(username=username,
                                                          addr=addr,
                                                          SSL=SSL,
                                                          pwd=pwd)
        if result == 1:
            return redirect(url_for("user.index"))
        else:
            ctx = {
                'msg': "添加失败"
            }
            return render_template("mail_account.html", **ctx)
    else:
        return render_template('mail_account.html')


@mail_app.route('/edit/<id>')
def edit(id):
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))

    ctx = {
        'pre': '../'
    }

    if id == 'new':
        return render_template('mail_send.html', **ctx)
    else:
        return render_template('mail_send.html', **ctx)


@mail_app.route('/send', methods=["POST"])
def send():
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))

    account = database.get_mail_account_by_username(username=username)

    send_to = request.form.get('sendTo')
    title = request.form.get('title')
    content = request.form.get('content')

    post_filenames = []
    sending_path = f'app/media/{username}/sending'
    if not os.path.exists(sending_path):
        os.makedirs(sending_path)

    for f in os.listdir(os.path.join(sending_path)):
        post_filenames.append(os.path.join(sending_path, f))

    To, send_to = generate_To_sendto(send_to)

    code = mail_utils.send_mail_by_smtp(user_addr=account.addr,
                                        pwd=account.pwd,
                                        SSL=account.SSL,
                                        port=465,
                                        receiver=send_to,
                                        From=f'{username} <{account.addr}>',
                                        To=To,
                                        title=default_title() + title,
                                        content=content,
                                        files=post_filenames)
    code2id = database.insert_mail_by_username(username=username,
                                               addr=account.addr,
                                               receiver=send_to,
                                               title=title,
                                               content=content,
                                               From=f'{username} <{account.addr}>',
                                               To=To,
                                               file=post_filenames)
    for rf in post_filenames:
        os.remove(rf)
    if code == 1:
        ctx = {
            'title': '发送成功',
            'content': '邮件已发送'
        }
        database.update_mail_type(mailid=code2id, args={
            'is_sended': True
        })
        return render_template('show_result.html', **ctx)
    else:
        ctx = {
            'title': '发送失败',
            'content': '邮件发送失败'
        }
        database.update_mail_type(mailid=code2id, args={
            'is_sended': False
        })
        return render_template('show_result.html', **ctx)


@mail_app.route('/draft', methods=["POST"])
def save_draft():
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))

    send_to = request.form.get('sendTo')
    title = request.form.get('title')
    content = request.form.get('content')

    To, send_to = generate_To_sendto(send_to)

    code2id = database.insert_simple_mail_by_username(username=username,
                                                      receiver=send_to,
                                                      title=title,
                                                      content=content,
                                                      To=To)
    if code2id != -1:
        database.update_mail_type(mailid=code2id, args={
            'is_draft': True
        })
        ctx = {
            'title': '保存成功',
            'content': '草稿保存成功'
        }
        return render_template('show_result.html', **ctx)
    else:
        ctx = {
            'title': '保存失败',
            'content': '草稿保存失败'
        }
        return render_template('show_result.html', **ctx)


@mail_app.route('/upFile', methods=["POST"])
def upFile():
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))

    image = request.files.get('file')
    filename = image.filename
    Time = datetime.datetime.now()

    basepath = f'{username}/{Time.year}/{Time.month}/{Time.day}'
    fullpath = f'app/media/{basepath}'
    if not os.path.exists(fullpath):
        os.makedirs(fullpath)
        fullpath = os.path.join(fullpath, filename)
    else:
        tfullpath = os.path.join(fullpath, filename)
        i = 0
        while os.path.exists(tfullpath):
            i += 1
            filename2 = f'({i}){filename}'
            tfullpath = os.path.join(fullpath, filename2)
        fullpath = tfullpath

    basepath = os.path.join(basepath, filename)
    image.save(fullpath)

    # for send
    tp_send = f'app/media/{username}/sending'
    if not os.path.exists(tp_send):
        os.makedirs(tp_send)
    shutil.copy(fullpath, os.path.join(tp_send, filename))

    jsdata = {
        "code": 0,  # 0表示成功，其它失败,
        "msg": "上传失败",  # 提示信息 一般上传失败后返回
        "data": {
            "src": '../../show/' + basepath,
            "title": filename  # 可选
        }
    }

    return jsonify(jsdata)


@mail_app.route('/inbox/<inds>', methods=['GET'])
def inbox(inds):
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))
    account = database.get_mail_account_by_username(username=username)

    indexlength = 6
    endpage = False

    topage = int(inds) - 1
    startindex = topage * indexlength

    received_mails = mail_utils.get_mails(server=account.SSL.replace('smtp', 'pop'),
                                          user=account.addr,
                                          pwd=account.pwd,
                                          username=username,
                                          startindex=startindex,
                                          indexlength=indexlength,
                                          download_files=False,
                                          endpage=endpage,
                                          default=get_server_pop_or_imap())

    # print(received_mails['mail_length'])
    # for mail in received_mails[f'mails']:
    #     print(mail['title'], mail['uid'])

    rets = {'mail_length': received_mails['mail_length'], 'mails': []}
    for index, d in enumerate(received_mails['mails']):
        isinstance(d, dict)
        mail_id = database.insert_receive_mail_by_username(username=username,
                                                           addr=account.addr,
                                                           receiver=str(d['from']).split(';'),
                                                           title=d['title'],
                                                           From=d['from'],
                                                           To=d['to'],
                                                           uid=d['uid'].split(' ')[-1],
                                                           content=d['content'],
                                                           file=d['files'])
        d['mail_id'] = mail_id
        d['is_star'] = database.get_mail_star(mailid=int(mail_id))
        if not database.get_mail_deleted(mailid=mail_id):
            rets['mails'].append(d)
        else:
            rets['mail_length'] -= 1

    mp, mpd = divmod(rets['mail_length'], indexlength)
    rets['maxpages'] = mp if mpd == 0 else mp + 1
    rets['curpage'] = int(inds)
    rets['mails'] = rets['mails'][:indexlength]
    rets['purl'] = '/mail/inbox'
    return render_template('mail_inbox.html', **rets)


@mail_app.route('/star_mail/<mailid>', methods=['POST'])
def star_mail(mailid):
    star = database.get_mail_star(mailid=int(mailid))
    if star is None:
        return

    args = {
        'is_star': not star
    }
    database.update_mail_type(mailid=int(mailid), args=args)

    return '收藏成功', 200


@mail_app.route('/mark_sended/', methods=['POST'])
def mark_sended():
    mail_ids = request.form.get("mailidlist")

    mlist = mail_ids.split(',')
    for id in mlist:
        database.update_mail_type(mailid=int(id), args={
            'is_sended': True
        })

    return '标记成功', 200


@mail_app.route('/mark_unsended/', methods=['POST'])
def mark_unsended():
    mail_ids = request.form.get("mailidlist")

    mlist = mail_ids.split(',')
    for id in mlist:
        database.update_mail_type(mailid=int(id), args={
            'is_sended': False
        })

    return '标记成功', 200


@mail_app.route('/mark_deleted/', methods=['POST'])
def mark_deleted():
    mail_ids = request.form.get("mailidlist")

    mlist = mail_ids.split(',')
    for id in mlist:
        database.update_mail_type(mailid=int(id), args={
            'is_deleted': True
        })

    return '删除成功', 200


@mail_app.route('/unmark_deleted/', methods=['POST'])
def unmark_deleted():
    mail_ids = request.form.get("mailidlist")

    mlist = mail_ids.split(',')
    for id in mlist:
        database.update_mail_type(mailid=int(id), args={
            'is_deleted': False
        })

    return '恢复成功', 200


@mail_app.route('/mail_delete/', methods=['POST'])
def mail_delete():
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))
    account = database.get_mail_account_by_username(username=username)

    mail_ids = request.form.get("mailidlist")
    mlist = mail_ids.split(',')

    indexs = []
    for ml in mlist:
        index, id = ml.split(';')
        indexs.append(index)
        database.delete_mail_by_id(mailid=int(id))

    mail_utils.delete_mail(
        server=account.SSL.replace('smtp', 'pop'),
        user=account.addr,
        pwd=account.pwd,
        ids=indexs,
        default=get_server_pop_or_imap()
    )

    return '删除邮件成功', 200


@mail_app.route('/download', methods=['POST'])
def download_mail_file():
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))
    account = database.get_mail_account_by_username(username=username)

    mail_index = [request.form.get("mail_ids").split(';')[0]]

    paths = mail_utils.download_mail_files(
        server=account.SSL.replace('smtp', 'pop'),
        user=account.addr,
        pwd=account.pwd,
        username=username,
        indexs=mail_index,
        default=get_server_pop_or_imap()
    )
    links = []
    for p in paths:
        links.append(p.replace('app/media/', '/show/'))

    return jsonify({
        'mailfiles': links
    })


@mail_app.route('/star_box/<inds>', methods=['GET'])
def star_box(inds):
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))

    indexlength = 6
    topage = int(inds) - 1
    startindex = topage * indexlength

    rets = database.get_star_mails(username=username)
    rets['mails'] = rets['mails'][startindex:]

    mp, mpd = divmod(rets['mail_length'], indexlength)
    rets['maxpages'] = mp if mpd == 0 else mp + 1
    rets['curpage'] = int(inds)
    rets['mails'] = rets['mails'][:indexlength]
    rets['purl'] = '/mail/star_box'
    return render_template('mail_star_inbox.html', **rets)


@mail_app.route('/draft_box/<inds>', methods=['GET'])
def draft_box(inds):
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))

    indexlength = 6
    topage = int(inds) - 1
    startindex = topage * indexlength

    rets = database.get_draft_mails(username=username)
    rets['mails'] = rets['mails'][startindex:]

    mp, mpd = divmod(rets['mail_length'], indexlength)
    rets['maxpages'] = mp if mpd == 0 else mp + 1
    rets['curpage'] = int(inds)
    rets['mails'] = rets['mails'][:indexlength]
    rets['purl'] = '/mail/draft_box'
    return render_template('mail_draft_box.html', **rets)


@mail_app.route('/mail_db_delete/', methods=['POST'])
def mail_db_delete():
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))

    mail_ids = request.form.get("mailidlist")
    mlist = mail_ids.split(',')

    indexs = []
    for ml in mlist:
        index, id = ml.split(';')
        indexs.append(index)
        database.delete_mail_by_id(mailid=int(id))

    return '删除草稿成功', 200


@mail_app.route('/sended_box/<inds>', methods=['GET'])
def sended_box(inds):
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))

    indexlength = 6
    topage = int(inds) - 1
    startindex = topage * indexlength

    rets = database.get_sended_mails(username=username)
    rets['mails'] = rets['mails'][startindex:]

    mp, mpd = divmod(rets['mail_length'], indexlength)
    rets['maxpages'] = mp if mpd == 0 else mp + 1
    rets['curpage'] = int(inds)
    rets['mails'] = rets['mails'][:indexlength]
    rets['purl'] = '/mail/sended_box'
    return render_template('mail_sended_box.html', **rets)


@mail_app.route('/deleted_box/<inds>', methods=['GET'])
def deleted_box(inds):
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))

    indexlength = 6
    topage = int(inds) - 1
    startindex = topage * indexlength

    rets = database.get_deleted_mails(username=username)
    rets['mails'] = rets['mails'][startindex:]

    mp, mpd = divmod(rets['mail_length'], indexlength)
    rets['maxpages'] = mp if mpd == 0 else mp + 1
    rets['curpage'] = int(inds)
    rets['mails'] = rets['mails'][:indexlength]
    rets['purl'] = '/mail/deleted_box'
    return render_template('mail_delete_box.html', **rets)


@mail_app.route('/group_box/<inds>', methods=['GET'])
def group_box(inds):
    username = session.get('username', '')
    if username == '':
        return redirect(url_for('user.index'))

    indexlength = 6
    topage = int(inds) - 1
    startindex = topage * indexlength

    rets = database.get_group_mails(username=username)
    rets['mails'] = rets['mails'][startindex:]

    mp, mpd = divmod(rets['mail_length'], indexlength)
    rets['maxpages'] = mp if mpd == 0 else mp + 1
    rets['curpage'] = int(inds)
    rets['mails'] = rets['mails'][:indexlength]
    rets['purl'] = '/mail/group_box'
    return render_template('mail_group_box.html', **rets)
