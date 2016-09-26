# -*- coding:utf-8 -*-
from mysql_db import db
from flask_login import UserMixin,AnonymousUserMixin
from . import login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from markdown import markdown
import bleach

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ACTICLES = 0x04 # 写原创文章
    MODERATE_COMMENTS = 0x08 # 查处他人发表的不当评论,MODERATE是协管员
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    default = db.Column(db.Boolean,default=False,index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User',backref='role',lazy='dynamic') # lazy='dynamic'禁止自动查询

    @staticmethod
    def insert_roles():
        roles = {
            'User':(Permission.FOLLOW | Permission.COMMIT | Permission.WRITE_ACTICLES,True),
            'Moderator':(Permission.FOLLOW | Permission.COMMIT | Permission.WRITE_ACTICLES | Permission.MODERATE_COMMENTS,False),
            'Administrator':(0xff,False)
        }
        for r in roles:
            role = Role.query.filter_by(_name = r).first()
            # 如果数据库里没有此角色
            if role is None:
                role = Role(_name = r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

class Rizhi(db.Model):
    __tablename__ = 'rizhi'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String,nullable=False)
    txt = db.Column(db.Text,nullable=False)
    fenlei = db.Column(db.String)
    dt = db.Column(db.DateTime)

    comments = db.relationship('Comment',backref='post',lazy='dynamic')

class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String,nullable=False)
    username = db.Column(db.String,nullable=False)
    confirmed = db.Column(db.Boolean,default=False)
    passwd = db.Column(db.String,nullable=False)
    liuyanban = db.relationship('Liuyanban',backref='user')
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default=datetime.utcnow)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

    comments = db.relationship('Comment',backref='author',lazy='dynamic') # backref给Comment一个author属性

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    # 此方法生成令牌，生效一小时
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm': self.id})

    # 此方法检验令牌
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        # 检查令牌中的id 是否和存储在current_user 中的已登录用户匹配
        if data.get('confirm') != self.id:
            return False
        # 如果检验通过，设confirmed为true
        self.confirmed = True
        db.session.add(self)
        return True

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.passwd = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.passwd,password)

    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        # 如果创建基类对象后还没定义角色,self.role是Role给User赋予的属性
        if self.role is None:
            # 根据电子邮件地址
            if self.email == current_app.config['ME80_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            # 如果角色没有设为管理员账户
            if self.role is None:
                # 将角色设为默认账户
                self.role = Role.query.filter_by(default=True).first()

    def can(self,permissions):
        # 如果角色中包含请求的所有权限位，则返回True
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

# 继承自Flask-Login 中的AnonymousUserMixin 类
class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False

    def is_administrator(self):
        return False

# 设为用户未登录时current_user 的值
login_manager.anonymous_user = AnonymousUser

class Liuyanban(db.Model):
    __tablename__ = 'liuyanban'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String)
    txt = db.Column(db.Text,nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))

class Comment(db.Model):
    __tablename__='comments'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow())
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer,db.ForeignKey('rizhi.id'))
    username = db.Column(db.String)

    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags = ['a','abbr','acronym','b','code','em','i','strong']
        target.body_html = bleach.linkify(bleach.clean(markdown(value,output_format='html'),tags=allowed_tags,strip=True))

db.event.listen(Comment.body,'set',Comment.on_changed_body)

class CommentsToComment(db.Model):
    __tablename__ = 'commentstocomment'
    id =db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    follow_comment_id = db.Column(db.Integer,db.ForeignKey('comments.id'))
    username = db.Column(db.String)
    tousername = db.Column(db.String)