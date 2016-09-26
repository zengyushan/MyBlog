# -*- coding:utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User, Role
from flask_pagedown.fields import PageDownField


class LoginForm(Form):
    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    # remember_me = BooleanField('Keep me logged in')
    submit = SubmitField(u'登录')


class RegistrationForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名：', validators=[DataRequired(), Length(1, 64),
                                                Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, u'用户名只能有字母，数字，点和下划线')])
    # EqualTo验证两次输入的密码是否一致
    password = PasswordField(u'密码：', validators=[DataRequired(), EqualTo('password2', message=u'两次输入的密码不匹配！')])
    password2 = PasswordField(u'再次输入密码：', validators=[DataRequired()])
    submit = SubmitField(u'注册')

    # 表单类中定义了以validate_开头且后面跟着字段名的方法，这个方法就和常规的验证函数一起调用
    def validate_email(self, field):
        # 如果数据库中存在此email
        if User.query.filter_by(email=field.data).first():
            # 则抛出异常，其参数就是错误消息
            raise ValidationError(u'Email已被注册.')
            # raise ValidationError(User.query.filter_by(email=field.data).first().email)

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已经被使用.')


class EditProfileForm(Form):
    name = StringField(u'真实姓名', validators=[Length(0, 64)])
    location = StringField(u'所在地', validators=[Length(0, 64)])
    about_me = TextAreaField(u'自我介绍')
    submit = SubmitField(u'提交')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 64),
                                               Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, u'用户名只能包含字母, 数字,点或者下划线,并以字母开头')])
    confirmed = BooleanField(u'认证')
    role_id = SelectField(u'角色', coerce=int)
    name = StringField(u'姓名', validators=[Length(0, 64)])
    location = StringField(u'所在地', validators=[Length(0, 64)])
    about_me = TextAreaField(u'自我介绍')
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role_id.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError(u'Email已经被使用了.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已经被使用了.')


class PinglunForm(Form):
    title = PageDownField(u'更改标题', validators=[DataRequired()])
    body = PageDownField(u'更改文章', validators=[DataRequired()])
    submit = SubmitField(u'提交')


class CommentForm(Form):
    body = TextAreaField(u'填写评论', validators=[DataRequired()])
    submit = SubmitField(u'提交')


class MessageBoardForm(Form):
    txt = TextAreaField(u'写留言...', validators=[DataRequired()])
    submit = SubmitField(u'提交')

class NewPostForm(Form):
    title = StringField(u'标题',validators=[DataRequired()])
    txt = TextAreaField(u'文章',validators=[DataRequired()])
    submit = SubmitField(u'提交')

# class CommentToCommentForm(Form):
#     body = TextAreaField(u'回复',validators=[DataRequired()])
#     submit = SubmitField(u'提交')