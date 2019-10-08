import os

# contains application-wide configuration, and is loaded in __init__.py

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret' # TODO: Use this with wtforms
    DATABASE = 'database.db'
    UPLOAD_PATH = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {'jpg', 'png', 'gif'} # Might use this at some point, probably don't want people to upload any file type
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
