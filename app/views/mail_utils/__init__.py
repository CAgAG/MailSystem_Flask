from . import mail_utils_smtp, mail_utils_pop3, mail_utils_imap


def send_mail_by_smtp(user_addr: str, pwd: str, SSL: str, port: int,
                      receiver: list,
                      From: str, To: str, title: str, content: str, files: list):
    return mail_utils_smtp.send_mail_by_smtp(user_addr=user_addr,
                                             pwd=pwd,
                                             SSL=SSL,
                                             port=port,
                                             receiver=receiver,
                                             From=From,
                                             To=To,
                                             title=title,
                                             content=content,
                                             files=files)


def default_163_send_by_smtp():
    return mail_utils_smtp.default_163_send_by_smtp()


def get_mail_length(server: str, user: str, pwd: str, default='pop') -> int:
    if default == 'pop':
        return mail_utils_pop3.get_mail_length_pop3(server=server, user=user, pwd=pwd)
    else:
        server = server.replace('pop', 'imap')
        return mail_utils_imap.get_mail_length_imap(server=server, user=user, pwd=pwd)


def get_mails(server: str, user: str, pwd: str, username: str,
              startindex=0, indexlength=9, endpage=False, download_files=False, default='pop') -> dict:
    if default == 'pop':
        return mail_utils_pop3.get_mail_by_pop3(server=server,
                                                user=user, pwd=pwd,
                                                username=username, startindex=startindex,
                                                indexlength=indexlength, endpage=endpage,
                                                download_files=download_files)
    else:
        server = server.replace('pop', 'imap')
        return mail_utils_imap.get_mail_by_imap(server=server,
                                                user=user, pwd=pwd,
                                                username=username, startindex=startindex,
                                                indexlength=indexlength, endpage=endpage,
                                                download_files=download_files)


def download_mail_files(server: str, user: str, pwd: str, username: str, indexs: list, default='pop'):
    if default == 'pop':
        return mail_utils_pop3.download_mail_files_by_pop3(server=server, user=user, pwd=pwd,
                                                           username=username, indexs=indexs)
    else:
        server = server.replace('pop', 'imap')
        return mail_utils_imap.download_mail_files_by_imap(server=server, user=user, pwd=pwd,
                                                           username=username, indexs=indexs)


def delete_mail(server: str, user: str, pwd: str, ids: list, default='pop'):
    if default == 'pop':
        return mail_utils_pop3.delete_mail_by_pop3(server=server, user=user, pwd=pwd, ids=ids)
    else:
        server = server.replace('pop', 'imap')
        return mail_utils_imap.delete_mail_by_imap(server=server, user=user, pwd=pwd, ids=ids)


def default_get_mails(default='pop'):
    if default == 'pop':
        return mail_utils_pop3.default_get_mail_by_pop3()
    else:
        return mail_utils_imap.default_get_mail_by_imap()
