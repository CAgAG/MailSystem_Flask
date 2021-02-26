from app import app
from app.views.user import user
from app.views.mail import mail_app
from app.views.calendar import calendar

# 注册蓝图
app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(mail_app, url_prefix='/mail')
app.register_blueprint(calendar, url_prefix='/calendar')
