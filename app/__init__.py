from flask import Flask, g
from config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin
from flask_wtf.csrf import CSRFProtect
import sqlite3
import os


# create and configure app
csrf = CSRFProtect()
app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)
csrf.init_app(app)
# load and configure flask_login authentication
login = LoginManager(app)
login.login_view = 'index'


class User(UserMixin):
    pass


@login.user_loader
def load_user(user_id):
    query = 'SELECT * FROM Users WHERE id=?;'
    user_row = prepared_query(query, (user_id,), one=True)
    if user_row is None:
        return None
    user = User()
    user.id = user_row['id']
    user.username = user_row['username']
    return user


# get an instance of the db
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

# initialize db for the first time
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# prepared sql queries
def safe_query(preparedQuery, tupleArgs, one=False):
    db = get_db()
    cursor = db.execute(preparedQuery, tupleArgs)
    rv = cursor.fetchall()
    cursor.close()
    db.commit()
    return (rv[0] if rv else None) if one else rv

# perform generic query, not very secure yet
def unsafe_query(unpreparedQuery, one=False):
    db = get_db()
    cursor = db.execute(unpreparedQuery)
    rv = cursor.fetchall()
    cursor.close()
    db.commit()
    return (rv[0] if rv else None) if one else rv

# TODO: Add more specific queries to simplify code

# automatically called when application is closed, and closes db connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# initialize db if it does not exist
if not os.path.exists(app.config['DATABASE']):
    init_db()

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH'])

from app import routes