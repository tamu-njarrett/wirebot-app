from datetime import datetime, date
from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from sqlalchemy import select
from wirebot import db
from wirebot.models import Post, Photo, Location
from wirebot.posts.forms import PostForm, PictureForm
from wirebot.posts.utils import save_picture_post, save_picture_plant, save_picture_ftp


posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        if form.picture.data:
            save_picture_post(form.picture.data, post)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post',form=form, legend='New Post')


# url for specific posts
@posts.route("/post/<int:post_id>")   # expecitng post id to be integer
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',form=form, legend='Update post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted!', 'danger')
    return redirect(url_for('main.home'))

@posts.route("/pictures", methods=['GET', 'POST'])
@login_required
def pictures():
    form = PictureForm()
    if form.validate_on_submit():
        if form.picture_list.data:
            new_photos = save_picture_plant(form.picture_list.data) # Getting back list of Photo class objects
        for pic in new_photos:
            db.session.add(pic)
            db.session.commit()
        flash('Your pictures have been added!', 'success')
        return redirect(url_for('posts.pictures'))

    new_ftp_photos = save_picture_ftp()
    for pic in new_ftp_photos:
        db.session.add(pic)
        db.session.commit()
    
    # dates = list(Photo.query.order_by(Photo.date_uploaded.desc()).with_entities(Photo.date_uploaded).all())
    # new_dates = []
    # for picture_date in dates:

    #     y_m_d = picture_date.date()
    #     if y_m_d in new_dates:
    #         pass
    #     else:
    #         new_dates += y_m_d

    # print(new_dates)

    page = request.args.get('page', 1, type=int)
    photos = Photo.query.order_by(Photo.date_uploaded.desc()).paginate(page=page, per_page=12)
    return render_template('pictures.html', title='Pictures', form=form, photos=photos, legend='Pictures')

