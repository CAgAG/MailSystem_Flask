# 邮箱
# MAIL_SERVER = "smtp.163.com"
# MAIL_PORT = "587"
# MAIL_USE_TLS = True
# MAIL_USERNAME = "xx@163.com"
# MAIL_PASSWORD = "xx" #生成的授权码
# MAIL_DEFAULT_SENDER = "xx@163.com"

# MAIL_SERVER	localhost	电子邮件服务器的主机名或IP地址
# MAIL_PORT	587	电子邮件服务器的端口
# MAIL_USE_TLS	False	启用传输层安全协议
# MAIL_USE_SSL	False	启用安全套接层协议
# MAIL_USERNAME	None	邮件账户的用户名
# MAIL_PASSWORD	None	邮件账户的密码

# ====================================================
# 数据库
# 设置连接数据库的URL
SQLALCHEMY_DATABASE_URI = 'mysql://test:123456@127.0.0.1:3306/flask_exp'
# 数据库和模型类同步修改
SQLALCHEMY_TRACK_MODIFICATIONS = True
# 查询时会显示原始SQL语句
SQLALCHEMY_ECHO = True

# ====================================================
# session
SECRET_KEY = 'netexp'

