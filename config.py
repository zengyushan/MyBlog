# -*- coding:utf-8-*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))
# 此基类含有通用配置
class Config:
    # os.environ.get('SECRET_KEY')是系统默认值
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    ME80_MAIL_SUBJECT_PREFIX = '[ME80]'
    ME80_MAIL_SENDER = 'ME80 <zyszys805@139.com>'
    ME80_ADMIN = os.environ.get('ME80_ADMIN') or 'me80'
    ME80_COMMENTS_PER_PAGE = 3
    ME80_POSTS_PER_PAGE = 4
    ME80_MESSAGEBOARD_PER_PAGE = 3
    # 参数app是程序实例
    # 此方法中，可以执行对当前环境的配置初始化
    @staticmethod
    def init_app(app):
        pass
# 定义专用配置
class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.139.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USERNAME = 'zyszys805@139.com'
    MAIL_PASSWORD = '57yoaa6nby'
    # 此类，和下面两个类的SQLALCHEMY_DATABASE_URI都不一样，确保程序在不同的环境中运行(数据库都不一样)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql://root:12345@localhost/blog'
# 定义专用配置
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'mysql://root:12345@localhost/blog'
# 定义专用配置
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://root:12345@localhost/blog'
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}