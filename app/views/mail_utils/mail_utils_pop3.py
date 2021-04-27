import os
import poplib

import email
from email.header import decode_header


def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


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


def get_mail_length_pop3(server: str, user: str, pwd: str) -> int:
    pop3 = poplib.POP3(server)
    pop3.user(user)
    pop3.pass_(pwd)
    _, mails, _ = pop3.list()
    return len(mails)


def get_mail_by_pop3(server: str, user: str, pwd: str, username: str,
                     startindex=0, indexlength=9, endpage=False, download_files=False) -> dict:
    pop3 = poplib.POP3(server)
    pop3.user(user)
    pop3.pass_(pwd)

    # # 可选:打印POP3服务器的欢迎文字:
    # print(pop3.getwelcome())
    # # stat()返回邮件数量和占用空间:
    # print('Messages: %s. Size: %s' % pop3.stat())
    # list()返回所有邮件的编号:
    _, mails, _ = pop3.list()
    ret = {}
    # 可以查看返回的列表类似['1 82923', '2 2184', ...]
    # print(mails)
    # 获取最新一封邮件, 注意索引号从1开始:
    length = len(mails)
    ret['mail_length'] = length
    ret['mails'] = []

    startindex = length - startindex
    # endindex = startindex - indexlength
    endindex = 0
    if endpage:
        startindex = length // indexlength
        endindex = 0

    for index in range(length):
        if (length - index) > startindex:
            continue
        if (length - index) <= endindex or startindex < 0:
            break

        _, lines, _ = pop3.retr(length - index)
        # lines存储了邮件的原始文本的每一行,
        # 可以获得整个邮件的原始文本:
        msg_content = b'\r\n'.join(lines)
        # 稍后解析出邮件:
        msg = email.parser.BytesParser(policy=email.policy.default).parsebytes(msg_content)
        # 可以根据邮件索引号直接从服务器删除邮件:
        ret2 = {}
        ret2['index'] = index
        ret2['uid'] = str(pop3.uidl(length - index))
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
                # # 要检测文本编码:
                # charset = guess_charset(msg)
                # if charset:
                #     content = content.decode(charset)
                ret2['content'] += content
                # print(content)

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
    pop3.quit()
    return ret


def download_mail_files_by_pop3(server: str, user: str, pwd: str, username: str, indexs: list):
    """
    :param server: 服务器地址
    :param user: 用户邮箱地址
    :param pwd: 密码
    :param username: 用户名
    :param indexs: 邮件索引列表
    :return: 下载目录列表
    """
    pop3 = poplib.POP3(server)
    pop3.user(user)
    pop3.pass_(pwd)

    _, mails, _ = pop3.list()
    length = len(mails)
    download_paths = []
    for index in indexs:
        index = int(index)
        _, lines, _ = pop3.retr(length - index)
        e_uid = str(pop3.uidl(length - index)).strip().split(' ')[-1].replace("'", '')
        # lines存储了邮件的原始文本的每一行,
        # 可以获得整个邮件的原始文本:
        msg_content = b'\r\n'.join(lines)
        # 稍后解析出邮件:
        msg = email.parser.BytesParser(policy=email.policy.default).parsebytes(msg_content)

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
                if os.path.exists(fullpath):
                    continue

                with open(os.path.join(fullpath), 'wb') as f:
                    f.write(content)

    pop3.quit()
    return download_paths


def delete_mail_by_pop3(server: str, user: str, pwd: str, ids: list):
    """
        :param server: 服务器地址
        :param user: 用户邮箱地址
        :param pwd: 密码
        :param index: 删除的索引
        :return: 0: 失败, 1: 成功
    """
    pop3 = poplib.POP3(server)
    pop3.user(user)
    pop3.pass_(pwd)

    length, _ = pop3.stat()
    try:
        for i in ids:
            pop3.dele(length - int(i))
        pop3.quit()
    except Exception:
        return 0
    return 1


def default_get_mail_by_pop3():
    return get_mail_by_pop3(
        server='pop.163.com',
        user='15685134992@163.com',
        pwd='HSJKBVWZUUKPOOOK',
        username='a'
    )


if __name__ == '__main__':
    # code = default_163_send_by_smtp()
    # print(code)
    print(default_get_mail_by_pop3()['mails'])
