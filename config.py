import os
import random

# contains application-wide configuration, and is loaded in __init__.py

class Config(object):
    SECRET_KEY = os.urandom(64) or "b'\\xdc\\x9c\\x15\\xc2\\x15m\\xf1X5\\xc0\\xa8f\\n\\xe1H \\xa01\\x82\\xa29\\xfd\\xcfM\\xcb\\x8aFo(\\xb9\\xe8AZ\\xcb\\x98\\xb9\\xa2\\xf1\\x9a\\xa2\\xb4\\x04\\xb2\\x08eM\\x19\\xbb\\x0f\\xc4\\xc6\\xab\\x07\\xbb\\xb6\\xa9\\xec\\x12\\xac\\xc6\\xaal\\xc2\\x9c'" #os.environ.get('SECRET_KEY') or 'secret' # TODO: Use this with wtforms
    print(SECRET_KEY)
    DATABASE = 'database.db'
    UPLOAD_PATH = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {'jpg', 'png', 'gif'} # Might use this at some point, probably don't want people to upload any file type
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
