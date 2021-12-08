import os
from flask import render_template, url_for, flash, redirect, request, abort, send_from_directory
from fit4all import app, db, bcrypt
from fit4all.forms import AccountForm, RegistrationForm, LoginForm, PostForm, NoteForm, UpdateUserProfilePicForm
from fit4all.models import User, Post, Note
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from PIL import Image

@app.route("/")
def home():
    if current_user.is_authenticated:
        posts = Post.query.filter_by(user_id=current_user.id).all()
        posts.reverse()
        notes = Note.query.filter_by(note_user_id=current_user.id).all()
        return render_template('home.html', posts = posts, notes = notes)
    
    return register()

@app.route("/about")
def about():
    if current_user.is_authenticated:
        notes = Note.query.filter_by(note_user_id=current_user.id).all()
        return render_template('about.html', title = 'about', notes = notes)
    return render_template('about.html', title = 'about')

@app.route("/error404")
def error404():
    return render_template('error404.html', title = 'error404')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    notes = Note.query.filter_by(note_user_id=current_user.id).all()
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data, content = form.content.data, athlete = current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post created', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title = 'New Post', form = form,legend = 'Create Post', notes = notes)


@app.route("/post/<post_id>")
def post(post_id):
    notes = Note.query.filter_by(note_user_id=current_user.id).all()
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title = post.title, post = post, notes = notes)

@app.route("/post/<int:post_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    notes = Note.query.filter_by(note_user_id=current_user.id).all()
    post = Post.query.get_or_404(post_id)
    if post.athlete != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='edit Post', form=form, legend='edit Post', notes = notes)

@app.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.athlete != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/account/<int:user_id>")
@login_required
def account(user_id):
    notes = Note.query.filter_by(note_user_id=current_user.id).all()
    user = User.query.get_or_404(user_id)
    posts =Post. query.filter_by(user_id=user_id).all()
    posts.reverse()

    form = AccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        db.session.commit()
        flash('Your account picture has been updated!', 'success')
        return redirect(url_for('account'))

    userPostsNum = len(posts)

    if userPostsNum < 1:
        userPostsNum = 0
        
    profile_image = url_for('static', filename='profile_images/' + current_user.image_file)
    return render_template('account.html', user = user, notes = notes, profile_image = profile_image, userPostsnum = userPostsNum, posts = posts)


def save_picture(form_picture):
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account/<int:user_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_account(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id:
        abort(403)
    posts = Post.query.filter_by(user_id=current_user.id).all()
    for post in posts:
        db.session.delete(post)
    db.session.delete(user)
    db.session.commit()
    flash('Your account has been deleted!', 'success')
    return redirect(url_for('login'))


@app.route("/note/<note_id>")
def note(note_id):
    notes = Note.query.filter_by(note_user_id=current_user.id).all()
    note = Note.query.get_or_404(note_id)
    return render_template('note.html', note = note, notes = notes)


@app.route("/note/new", methods=['GET', 'POST'])
@login_required
def new_note():
    notes = Note.query.filter_by(note_user_id=current_user.id).all()
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(content = form.content.data, note_user_id = current_user.id)
        db.session.add(note)
        db.session.commit()
        flash('note created', 'success')
        return redirect(url_for('home'))
    return render_template('create_note.html', title = 'New note', form = form, legend = 'Create note', notes = notes)

@app.route("/note/<int:note_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    notes = Note.query.filter_by(note_user_id=current_user.id).all()
    note = Note.query.get_or_404(note_id)
    if note.note_user_id != current_user.id:
        abort(403)
    form = NoteForm()
    if form.validate_on_submit():
        note.content = form.content.data
        db.session.commit()
        flash('Your note has been updated!', 'success')
        return redirect(url_for('note', note_id=note.id))
    elif request.method == 'GET':
        form.content.data = note.content
    return render_template('create_note.html', title='edit note', form=form, legend='edit note', notes = notes)

@app.route("/note/<int:note_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_note(note_id):
    notes = Note.query.filter_by(note_user_id=current_user.id).all()
    note = Note.query.get_or_404(note_id)
    if note.note_user_id != current_user.id:
        abort(403)
    db.session.delete(note)
    db.session.commit()
    flash('Your note has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/exploreUsers")
def explore_users():
    if current_user.is_authenticated:
        users = User.query.all()
        users.reverse()
        notes = Note.query.filter_by(note_user_id=current_user.id).all()
        return render_template('explore_users.html', users = users, notes = notes)
    
    return register()

