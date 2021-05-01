import os
from imapclient import IMAPClient

import email
from email.parser import Parser


def guess_charset(msg):
    # 先从msg对象获取编码:
    charset = msg.get_charset()
    if charset is None:
        # 如果获取不到，再从Content-Type字段获取:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


def get_mail_by_imap(server: str, user: str, pwd: str, username: str,
                     startindex=0, indexlength=9, endpage=False, download_files=False) -> dict:
    server = IMAPClient(server, ssl=True, port=993)
    server.login(user, pwd)
    server.id_({"name": "IMAPClient", "version": "2.2.0"})
    server.select_folder('INBOX', readonly=True)

    msg_uid = server.search(['NOT', 'DELETED'])
    msg_dict = server.fetch(msg_uid, ['BODY[]'])

    length = len(msg_dict)
    ret = {}
    ret['mail_length'] = length
    ret['mails'] = []

    startindex = length - startindex
    # endindex = startindex - indexlength
    endindex = 0
    if endpage:
        startindex = length // indexlength
        endindex = 0

    for index, (message_id, message) in enumerate(reversed(msg_dict.items())):
        if (length - index) > startindex:
            continue
        if (length - index) <= endindex or startindex < 0:
            break

        msg = email.parser.BytesParser(policy=email.policy.default).parsebytes(message[b'BODY[]'])

        ret2 = {}
        ret2['index'] = index
        ret2['uid'] = str(message_id)
        # print('发件人', msg['from'])
        ret2['from'] = msg['from']
        ret2['receivers'] = msg['from']
        # print('收件人', msg['to'])
        ret2['to'] = msg['to']
        # print('时间', msg['date'])
        ret2['date'] = msg['date']
        # print('主题', msg['subject'])
        ret2['title'] = msg['subject']

        # print('第一个收件人用户名', msg['to'].addresses[0].username)
        ret2['first_receiver'] = msg['to'].addresses[0].username if not isinstance(msg['to'], str) else '保密'
        # print('第一个发件人用户名', msg['from'].addresses[0].username)
        ret2['first_sender'] = msg['from'].addresses[0].username
        ret2['content'] = ''
        ret2['files'] = []
        ret2['filenames'] = []

        for part in msg.walk():
            content_type = part.get_content_type()
            if 'text/html' == content_type:
                # HTML内容:
                content = part.get_content()
                # 要检测文本编码:
                ret2['content'] += content

            elif content_type == 'application/octet-stream':
                # 不是文本,作为附件处理:
                content = part.get_content()
                charset = guess_charset(msg)
                if charset:
                    content = content.decode(charset)
                filename = part.get_filename()
                filepath = f'app/media/{username}/received/'
                if not os.path.exists(filepath):
                    os.makedirs(filepath)

                fullpath = f'{filepath}/{filename}'
                i = 1
                while os.path.exists(fullpath):
                    fullpath = f'{filepath}/({i}){filename}'
                    i += 1

                if download_files:
                    # print('附件名称:', filename)
                    with open(os.path.join(fullpath), 'wb') as f:
                        f.write(content)

                ret2['files'].append(fullpath)
                ret2['filenames'].append(filename)
        ret['mails'].append(ret2)
    server.logout()
    return ret


def download_mail_files_by_imap(server: str, user: str, pwd: str, username: str, indexs: list):
    """
    :param server: 服务器地址
    :param user: 用户邮箱地址
    :param pwd: 密码
    :param username: 用户名
    :param indexs: 邮件索引列表
    :return: 下载目录列表
    """
    server = IMAPClient(server, ssl=True, port=993)
    server.login(user, pwd)
    server.id_({"name": "IMAPClient", "version": "2.2.0"})
    server.select_folder('INBOX', readonly=True)

    msg_uid = server.search(['NOT', 'DELETED'])
    msg_dict = server.fetch(msg_uid, ['BODY[]'])

    download_paths = []
    for index, (message_id, message) in enumerate(reversed(msg_dict.items())):
        if str(index) not in indexs:
            continue
        msg = email.parser.BytesParser(policy=email.policy.default).parsebytes(message[b'BODY[]'])

        e_uid = message_id
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'application/octet-stream':
                # 不是文本,作为附件处理:
                content = part.get_content()
                charset = guess_charset(msg)
                if charset:
                    content = content.decode(charset)
                filename = part.get_filename()
                filepath = f'app/media/{username}/received/{e_uid}'
                if not os.path.exists(filepath):
                    os.makedirs(filepath)

                fullpath = f'{filepath}/{filename}'
                download_paths.append(fullpath)
                with open(os.path.join(fullpath), 'wb') as f:
                    f.write(content)
    server.logout()
    return download_paths


def delete_mail_by_imap(server: str, user: str, pwd: str, ids: list):
    """
    :param server: 服务器地址
    :param user: 用户邮箱地址
    :param pwd: 密码
    :param index: 删除的索引
    :return: 0: 失败, 1: 成功
    """
    server = IMAPClient(server, ssl=True, port=993)
    server.login(user, pwd)
    server.id_({"name": "IMAPClient", "version": "2.2.0"})
    server.select_folder('INBOX')

    msg_uid = server.search(['NOT', 'DELETED'])
    msg_dict = server.fetch(msg_uid, ['BODY[]'])
    try:
        for index, (message_id, message) in enumerate(reversed(msg_dict.items())):
            if str(index) in ids:
                server.delete_messages(message_id)
        server.logout()
    except Exception:
        return 0
    return 1


def get_mail_length_imap(server: str, user: str, pwd: str) -> int:
    server = IMAPClient(server, ssl=True, port=993)
    server.login(user, pwd)
    server.id_({"name": "IMAPClient", "version": "2.2.0"})
    server.select_folder('INBOX')

    msg_uid = server.search(['NOT', 'DELETED'])
    msg_dict = server.fetch(msg_uid, ['BODY[]'])
    return len(msg_dict)


def default_get_mail_by_imap():
    pass


if __name__ == '__main__':
    d = default_get_mail_by_imap()
    print(d)
