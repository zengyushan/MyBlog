# -*- coding:utf-8 -*-
from app import db
from app.mysql_db import db as newdb
from .. import auth
from . import main
from flask import render_template, redirect, request, url_for, flash, abort, current_app
from app.models import Rizhi, Liuyanban, User, Role, Permission, Comment
from ..auth.forms import LoginForm, RegistrationForm, EditProfileForm, EditProfileAdminForm, PinglunForm, CommentForm
from flask_login import login_user, logout_user, login_required, current_user
from ..email import send_email
from ..decorators import admin_required


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Rizhi.query.order_by(Rizhi.dt.desc()).paginate(page,
                                                                per_page=current_app.config['ME80_POSTS_PER_PAGE'],
                                                                error_out=False)
    rizhis = pagination.items
    if rizhis is None:
        return render_template('zhuye.html')
    else:
        return render_template('zhuye.html', rizhis=rizhis, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    # flash(u'您的资料已更新')
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    user = User.query.filter_by(username=current_user.username).first()
    name = user.name
    location = user.location
    about_me = user.about_me
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        newdb.session.add(current_user)
        newdb.session.commit()
        print user.name
        # 如果提交的资料与原来的有不一样的
        if form.name.data != name or form.location.data != location or form.about_me.data != about_me:
            flash(u'您的资料已更新')
        return redirect(url_for('main.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        # user.role_id = Role.query.get(form.role_id.data)
        user.role_id = form.role_id.data
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        newdb.session.add(user)
        newdb.session.commit()
        flash(u'profile已更新')
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role_id.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    rizhi = Rizhi.query.get_or_404(id)
    if current_user != User.query.filter_by(username='me80') and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PinglunForm()
    if form.validate_on_submit():
        rizhi.title = form.title.data
        rizhi.txt = form.body.data
        newdb.session.add(rizhi)
        newdb.session.commit()
        flash(u'文章已更新.')
        return redirect(url_for('main.rizhi', id=rizhi.id))
    form.body.data = rizhi.txt
    form.title.data = rizhi.title
    return render_template('edit_post.html', form=form)


@main.route('/rizhi/<int:id>', methods=['GET', 'POST'])
# @main.route('/rizhi/<int:id>/<int:comment_id>',methods=['GET','POST'])
def rizhi(id):
    rizhi = Rizhi.query.get_or_404(id)
    comment_to_post_form = CommentForm()

    # comment_to_comment_form = CommentToCommentForm()
    # # 如果对某条评论提交回复
    # if comment_to_comment_form.validate_on_submit():
    #     comment = Comment(body=comment_to_comment_form.body.data, author_id=current_user.id,
    #                       comment_follow_id=comment_id)
    #     newdb.session.add(comment)
    #     newdb.session.commit()
    #     return redirect(url_for('main.rizhi',id=id))

    # 如果对某篇日志提交评论
    if comment_to_post_form.validate_on_submit():
        comment = Comment(body=comment_to_post_form.body.data, post_id=id, username=current_user.username,
                          author=current_user._get_current_object())
        newdb.session.add(comment)
        newdb.session.commit()
        flash(u'你的评论已经提交')
        return redirect(url_for('main.rizhi', id=rizhi.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        # page是显示哪一页
        page = (Comment.query.filter_by(post_id=id).count() - 1) // current_app.config['ME80_COMMENTS_PER_PAGE'] + 1
        print page
    print 22222222222222222
    # 如果此日志还没有任何评论()
    if Comment.query.filter_by(post_id=id).all() == []:
        print 1111111111111111
        print Comment.query.filter_by(post_id=id).all()
        return render_template('rizhi.html', rizhi=rizhi, form=comment_to_post_form, pagination=None, id=id)

    pagination = Comment.query.filter_by(post_id=Comment.query.filter_by(post_id=id).first().post_id).order_by(
        Comment.timestamp.desc()).paginate(page, per_page=current_app.config[
        'ME80_COMMENTS_PER_PAGE'], error_out=False)

    return render_template('rizhi.html', rizhi=rizhi, form=comment_to_post_form, pagination=pagination, id=id)
