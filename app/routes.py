import sqlite3

from flask import render_template, flash, redirect, url_for, request, make_response
from flask_login import logout_user, login_required, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, prepared_query, unsafe_query, load_user
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from datetime import datetime
from flask_wtf.csrf import CSRFError
import os


# this file contains all the different routes, and the logic for communicating with the database

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = IndexForm()
    if form.login.validate_on_submit() and form.login.submit.data:
        preparedQuery = 'SELECT * FROM Users WHERE username=?;'
        user = prepared_query(preparedQuery, (form.login.username.data.lower(),), one=True)
        if user is None:
            flash('Sorry, invalid credentials!')
        elif check_password_hash(user['password'], form.login.password.data):
            app_user = load_user(int(user['id']))
            login_user(app_user)
            return redirect(url_for('stream'))
        else:
            flash('Sorry, invalid credentials!')

    elif form.register.validate_on_submit() and form.register.submit.data:
        preparedQuery = 'SELECT * FROM Users WHERE username=?;'
        existing_user = prepared_query(preparedQuery, (form.register.username.data.lower(),), one=True)

        if existing_user is not None:
            flash('Sorry, invalid username!')
        elif form.register.password.data != form.register.confirm_password.data:
            flash('Passwords do not match!')
        else:
            preparedQuery = 'INSERT INTO Users (username, first_name, last_name, password) VALUES(?,?,?,?);'
            prepared_query(preparedQuery, (form.register.username.data.lower(), form.register.first_name.data,
                                         form.register.last_name.data,
                                         generate_password_hash(form.register.password.data)))
            return redirect(url_for('index'))
    return render_template('index.html', title='Welcome', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('index'))


# content stream page
@app.route('/stream', methods=['GET', 'POST'])
@login_required
def stream():
    form = PostForm()
    preparedQuery = 'SELECT * FROM Users WHERE id=?;'
    user = prepared_query(preparedQuery, (current_user.id,), one=True)
    canSubmit = True
    if form.validate_on_submit():
        if form.image.data:
            if allowed_file(form.image.data.filename):
                path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
                form.image.data.save(path) 
            else:
                canSubmit = False
                flash("Illegal file extension!")
        if canSubmit:
            preparedQuery = 'INSERT INTO Posts (u_id, content, image, creation_time) VALUES(?, ?, ?, ?);'
            prepared_query(preparedQuery, (
                user['id'], form.content.data, form.image.data.filename, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        return redirect(url_for('stream'))

    preparedQuery = 'SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc ' \
                  'FROM Posts AS p JOIN Users AS u ON u.id=p.u_id ' \
                  'WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id=?) ' \
                  'OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id=?) ' \
                  'OR p.u_id=? ' \
                  'ORDER BY p.creation_time DESC;'
    posts = prepared_query(preparedQuery, (current_user.id, current_user.id, current_user.id))
    return render_template('stream.html', title='Stream', form=form, posts=posts)


# comment page for a given post and user.
@app.route('/comments/<int:p_id>', methods=['GET', 'POST'])
@login_required
def comments(p_id):
    form = CommentsForm()
    if form.validate_on_submit():
        preparedQuery = 'INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES(?, ?, ?, ?);'
        prepared_query(preparedQuery, (p_id, current_user.id, form.comment.data, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

    preparedQuery = 'SELECT * FROM Posts WHERE id=?;'
    post = prepared_query(preparedQuery, (p_id,), one=True)

    all_comments = unsafe_query(
        'SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id={} ORDER BY c.creation_time DESC;'.format(
            p_id))
    return render_template('comments.html', title='Comments', form=form, post=post, comments=all_comments)


# page for seeing and adding friends
@app.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
    form = FriendsForm()
    preparedQuery = 'SELECT * FROM Users WHERE id=?;'
    user = prepared_query(preparedQuery, (current_user.id,), one=True)
    if form.validate_on_submit():
        preparedQuery = 'SELECT * FROM Users WHERE username=?;'
        friend = prepared_query(preparedQuery, (form.username.data.lower(),), one=True)
        if friend is None:
            flash('User does not exist')
        else:
            try:
                preparedQuery = 'INSERT INTO Friends (u_id, f_id) VALUES(?, ?);'
                prepared_query(preparedQuery, (user['id'], friend['id']))
            except sqlite3.IntegrityError:
                flash('Already friends')
    preparedQuery = 'SELECT * FROM Friends AS f ' \
                  'JOIN Users as u ON f.f_id=u.id ' \
                  'WHERE f.u_id=? AND f.f_id !=?  ;'
    all_friends = prepared_query(preparedQuery, (current_user.id, current_user.id))
    return render_template('friends.html', title='Friends', friends=all_friends, form=form)


# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    username = username.lower()
    preparedQuery = 'SELECT * FROM Users WHERE username=?;'
    user = prepared_query(preparedQuery, (username,), one=True)

    # viewing current_user's own profile
    if username == current_user.username:
        form = ProfileForm(user)
        if form.validate_on_submit():
            app.logger.info('failed to log in')
            preparedQuery = 'UPDATE Users ' \
                          'SET education=?, employment=?, music=?, movie=?, nationality=?, birthday=? ' \
                          'WHERE id=?;'
            prepared_query(preparedQuery, (
                form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data,
                form.birthday.data, current_user.id))
            return redirect(url_for('profile', username=username))
        return render_template('profile.html', title='Profile', user=user, form=form)
    else:
        return render_template('profile.html', title='Profile', user=user)


@app.after_request
def add_security_headers(resp):
    resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
    resp.headers['X-XSS-Protection'] = 1
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    return resp

@app.errorhandler(Exception)
def handle_error(e):
    return render_template('error.html')

#check if file has an allowed extension
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
