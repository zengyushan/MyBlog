# -*- coding:utf-8 -*-
from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

# 此为工厂函数，config_name是配置名
def create_app(config_name):
    app = Flask(__name__)
    # from_object用来导入config.py(上部分的代码)中的配置类
    # 配置对象config[config_name]通过名字从config字典(上部分代码)中选择
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    # 附加路由和自定义的错误页面
    # from .main import main as main_blueprint
    # app.register_blueprint(main_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint,url_prefix='/auth')
    app.register_blueprint(auth_blueprint)

    return app