# -*- coding:utf-8 -*-
from app import db
from app.mysql_db import db as newdb
from . import auth
from flask import render_template, redirect, request, url_for, flash, abort, current_app
from app.models import Rizhi, Liuyanban, User, Role, Permission, Comment, AnonymousUser, generate_password_hash,CommentsToComment
from forms import LoginForm, RegistrationForm, MessageBoardForm, EditProfileForm, EditProfileAdminForm, PinglunForm, \
    CommentForm,NewPostForm
from flask_login import login_user, logout_user, login_required, current_user
from ..email import send_email
from ..decorators import admin_required


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data,
                    passwd=generate_password_hash(form.password.data), role_id=3)
        newdb.session.add(user)
        newdb.session.commit()

        token = user.generate_confirmation_token()
        user_login = User.query.filter_by(email=form.email.data).first()
        # 上面刚注册了账户，这里就不用验证了，直接登录
        login_user(user_login)
        send_email(user_login.email, u'确认你的账户', '/email/confirm', user=user_login, token=token)
        # flash(u'一封确认邮件已经发送到你的email')
        return redirect(url_for('main.index'))
    return render_template('register.html', form=form)


@auth.route('/confirm/<string:token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    user = User.query.get(current_user.id)
    if current_user.confirm(token):
        user.comfirmed=True
        newdb.session.add(user)
        newdb.session.commit()
        flash(u'您已经认证了账户！')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    # 如果用户已登录
    if current_user.is_authenticated() == True:
        # 提交最后登录时间到数据库
        current_user.ping()
        # 如果令牌检验未通过 并且 请求端点不在认证蓝本中
        if not current_user.confirmed and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
            # 转到未认证的情况对应的视图函数
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    # 如果当前用户是匿名 或者 用户认证令牌通过
    if current_user.is_anonymous() or current_user.confirmed:
        return redirect(url_for('main.index'))
    # 转到未认证页面
    return render_template('unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, u'确认你的账户', 'email/confirm', user=current_user, token=token)
    # flash(u'一封新的邮件已经发送到你的邮箱')
    return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you have been logout')
    return redirect(url_for('main.index'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            # return redirect(request.args.get('next') or url_for('main.index'))
            return redirect(url_for('main.index'))
    flash(u'不合法的email或密码')
    return render_template('login.html', form=form)


@auth.route('/tech')
def tech():
    rizhi = Rizhi.query.filter_by(fenlei='tech').all()
    count = Rizhi.query.count()
    if rizhi is None:
        return render_template('tech.html')
    else:
        return render_template('tech.html', rizhi=rizhi, count=count)


@auth.route('/zatan')
def zatan():
    rizhi = Rizhi.query.filter_by(fenlei='zatan').all()
    count = Rizhi.query.count()
    if rizhi is None:
        return render_template('zatan.html')
    else:
        return render_template('zatan.html', rizhi=rizhi, count=count)


@auth.route('/share')
def share():
    rizhi = Rizhi.query.filter_by(fenlei='share').all()
    count = Rizhi.query.count()
    if rizhi is None:
        return render_template('share.html')
    else:
        return render_template('share.html', rizhi=rizhi, count=count)


@auth.route('/liuyan', methods=['GET', 'POST'])
def liuyan():
    liuyan = Liuyanban.query.all()
    count = Liuyanban.query.count()
    form = MessageBoardForm()
    # 如果用户未登录
    if current_user.is_authenticated() == False:
        # 如果数据库里没有任何留言数据
        if count == 0:
            return render_template('liuyanban.html', count=count)
        elif count > 0:
            # page是显示哪一页
            page = request.args.get('page', 1, type=int)
            pagination = Liuyanban.query.order_by(Liuyanban.id.desc()).paginate(page, per_page=current_app.config[
                'ME80_MESSAGEBOARD_PER_PAGE'], error_out=False)
            return render_template('liuyanban.html', liuyan=liuyan, count=count, pagination=pagination)
    if form.validate_on_submit():
        messageBoard = Liuyanban(txt=form.txt.data, username=current_user.username,
                                 user_id=current_user.id)
        print current_user.id
        newdb.session.add(messageBoard)
        newdb.session.commit()
        # flash(u'留言已提交')
        return redirect(url_for('auth.liuyan', page=-1))
    page = request.args.get('page', 1, type=int)
    print page
    if page == -1:
        page = (Liuyanban.query.count() - 1) // current_app.config['ME80_MESSAGEBOARD_PER_PAGE'] + 1
    pagination = Liuyanban.query.order_by(Liuyanban.id.desc()).paginate(page, per_page=current_app.config[
        'ME80_MESSAGEBOARD_PER_PAGE'], error_out=False)
    return render_template('liuyanban.html', renzheng=current_user.confirmed, liuyan=liuyan, count=count, form=form,
                           pagination=pagination)


@auth.route('/aboutme')
def aboutme():
    return render_template('aboutme.html')

@auth.route('/delete_post/<int:id>')
def delete_post(id):
    rizhi = Rizhi.query.filter_by(id=id).first_or_404()
    comment_all = Comment.query.filter_by(post_id=id).all()
    # 在循环中删除每一条评论数据
    for comment in comment_all:
        newdb.session.delete(comment)
    newdb.session.delete(rizhi)
    newdb.session.commit()
    return redirect(url_for('main.index'))

@auth.route('/delete_comment/<int:comment_id>/<int:post_id>')
def delete_comment(comment_id,post_id):
    comment = Comment.query.get_or_404(comment_id)
    newdb.session.delete(comment)
    newdb.session.commit()
    return redirect(url_for('main.rizhi',id=post_id))

@auth.route('/new_post',methods=['GET','POST'])
def new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        rizhi = Rizhi(title=form.title.data,txt=form.txt.data,fenlei='notClassified')
        newdb.session.add(rizhi)
        newdb.session.commit()
        return redirect(url_for('main.index'))
    return render_template('new_post.html',form=form)

# @auth.route('/comments_to_comment/<int:rizhi_id>/<int:to_comment_id>/<string:username>/<string:tousername>',methods=['GET','POST'])
# def comments_to_comment(rizhi_id,to_comment_id,username,tousername):
#     comment_to_comment_form = CommentToCommentForm()
#     if comment_to_comment_form.validate_on_submit():
#         # 注意这里 tousername是文章评论用户
#         ctc = CommentsToComment(body=comment_to_comment_form.body.data,follow_comment_id=to_comment_id,username=username,tousername=tousername)
#         newdb.session.add(ctc)
#         newdb.session.commit()
#     return redirect(url_for('main.rizhi',id=rizhi_id))

@auth.route('/delete_liuyan/<int:liuyan_id>',methods=['GET','POST'])
def delete_liuyan(liuyan_id):
    del_liuyan = Liuyanban.query.get_or_404(liuyan_id)
    newdb.session.delete(del_liuyan)
    newdb.session.commit()
    return redirect(url_for('auth.liuyan'))