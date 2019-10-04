from flask import render_template, flash, redirect, url_for, request, make_response
from app import app, prepared_query, unsafe_query
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
        queryString = 'SELECT * FROM Users WHERE username=?;'
        user = prepared_query(queryString, (form.login.username.data,), one=True)
        if user == None:
            flash('Sorry, this user does not exist!')
        elif user['password'] == form.login.password.data: 
            return redirect(url_for('stream', username=form.login.username.data))
        else:
            flash('Sorry, wrong password!')

    elif form.register.validate_on_submit() and form.register.submit.data: 
        queryString = 'INSERT INTO Users (username, first_name, last_name, password) VALUES(?,?,?,?);'
        prepared_query(queryString, (form.register.username.data, form.register.first_name.data,
         form.register.last_name.data, form.register.password.data))
        return redirect(url_for('index'))
    return render_template('index.html', title='Welcome', form=form)



# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
def stream(username):
    form = PostForm()
    queryString = 'SELECT * FROM Users WHERE username=?;'
    user = prepared_query(queryString, (username,), one=True)
    if form.validate_on_submit():
        if form.image.data:
            path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
            form.image.data.save(path)


        queryString = 'INSERT INTO Posts (u_id, content, image, creation_time) VALUES(?, ?, ?, ?);'
        prepared_query(queryString, (user['id'], form.content.data, form.image.data.filename, datetime.now().strftime("%d/%m/%Y %H:%M:%S")) )
        return redirect(url_for('stream', username=username))

    posts = unsafe_query('SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id={0}) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id={0}) OR p.u_id={0} ORDER BY p.creation_time DESC;'.format(user['id']))
    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)



# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
def comments(username, p_id):
    form = CommentsForm()
    if form.validate_on_submit():
        queryString = 'SELECT * FROM Users WHERE username=?;'
        user = prepared_query(queryString, (username,), one=True)
        queryString = 'INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES(?, ?, ? ?);'
        prepared_query(queryString, (p_id, user['id'], form.comment.data, datetime.now().strftime("%d/%m/%Y %H:%M:%S")) )

    queryString = 'SELECT * FROM Posts WHERE id=?;'
    post = prepared_query(queryString, (p_id,), one=True)

    all_comments = unsafe_query('SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id={} ORDER BY c.creation_time DESC;'.format(p_id))
    return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)



# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
def friends(username):
    form = FriendsForm()
    queryString = 'SELECT * FROM Users WHERE username=?;'
    user = prepared_query(queryString, (username,), one=True)
    if form.validate_on_submit():
        queryString = 'SELECT * FROM Users WHERE username=?;'
        friend = prepared_query(queryString, (form.username.data,), one=True)
        if friend is None:
            flash('User does not exist')
        else:
            queryString = 'INSERT INTO Friends (u_id, f_id) VALUES(?, ?);'
            prepared_query(queryString, (user['id'], friend['id']))
    
    all_friends = unsafe_query('SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id={} AND f.f_id!={} ;'.format(user['id'], user['id']))
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)



# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    form = ProfileForm()
    if form.validate_on_submit():
        app.logger.info('failed to log in')
        queryString = 'UPDATE Users SET education=?, employment=?, music=?, movie=?, nationality=?, birthday=? WHERE username=?;'
        prepared_query(queryString, (form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data, form.birthday.data, username))
        return redirect(url_for('profile', username=username))
    
    queryString = 'SELECT * FROM Users WHERE username=?;'
    user = prepared_query(queryString, (username,), one=True)
    return render_template('profile.html', title='profile', username=username, user=user, form=form)


@app.after_request
def add_security_headers(resp):
    resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
    resp.headers['X-XSS-Protection'] = 1
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    return resp

# @app.errorhandler(CSRFError)
# def handle_csrf_error(e):
#     return render_template('csrf_error.html', reason=e.description), 400