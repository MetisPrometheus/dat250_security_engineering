from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField, TextField
from wtforms.fields.html5 import DateField
from wtforms import validators

# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields
# TODO: Add validation, maybe use wtforms.validators??
# TODO: There was some important security feature that wtforms provides, but I don't remember what; implement it

class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={'placeholder': 'Username', 'maxlength' : 30}) 
    password = PasswordField('Password', render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember me') # TODO: It would be nice to have this feature implemented, probably by using cookies
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', render_kw={'placeholder': 'First Name', 'maxlength' : 50}, 
        validators=[validators.Regexp(r'^[\w]+$', message="Can only contain alphanumeric characters."), validators.InputRequired(), validators.Length(max=50)])

    last_name = StringField('Last Name', render_kw={'placeholder': 'Last Name', 'maxlength' : 80}, 
        validators=[validators.Regexp(r'^[\w]+$', message="Can only contain alphanumeric characters."), validators.InputRequired(), validators.Length(max=80)])

    username = StringField('Username', render_kw={'placeholder': 'Username', 'maxlength' : 30}, 
        validators=[validators.Regexp(r'^[\w]+$', message="Username can't contain spaces or special characters"), validators.Length(min=4, max=30)])

    password = PasswordField('Password', render_kw={'placeholder': 'Password'}, 
        validators=[validators.Regexp(r'^[\S]+$', message="Password can't contain spaces"), validators.InputRequired(), validators.Length(min=8)])
    confirm_password = PasswordField('Confirm Password', render_kw={'placeholder': 'Confirm Password'}, 
        validators=[validators.Regexp(r'^[\S]+$', message="Password can't contain spaces"), validators.InputRequired(), validators.Length(min=8)])

    submit = SubmitField('Sign Up')

class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)

class PostForm(FlaskForm):
    content = TextAreaField('New Post', render_kw={'placeholder': 'What are you thinking about?', 'maxlength' : 2000}, 
        validators=[validators.InputRequired(), validators.Length(max=2000)])
    image = FileField('Image')
    submit = SubmitField('Post')

class CommentsForm(FlaskForm):
    comment = TextAreaField('New Comment', render_kw={'placeholder': 'What do you have to say?', 'maxlength' : 2000}, 
        validators=[validators.InputRequired(), validators.Length(max=2000)])
    submit = SubmitField('Comment')

class FriendsForm(FlaskForm):
    username = StringField('Friend\'s username', render_kw={'placeholder': 'Username', 'maxlength' : 30}, 
        validators=[validators.Regexp(r'^[\w]+$', message="Usernames can't contain spaces or special characters"), 
        validators.InputRequired(), validators.Length(max=30)])
    submit = SubmitField('Add Friend')

class ProfileForm(FlaskForm):
    education = StringField('Education', render_kw={'placeholder': 'Highest education', 'maxlength' : 80},
        validators=[validators.InputRequired(), validators.Length(max=80),
        validators.Regexp(r'^[\w]+$', message="Can only contain alphanumeric characters.")])
    employment = StringField('Employment', render_kw={'placeholder': 'Current employment', 'maxlength' : 80}, 
        validators=[validators.InputRequired(), validators.Length(max=80),
        validators.Regexp(r'^[\w]+$', message="Can only contain alphanumeric characters.")])
    music = StringField('Favorite song', render_kw={'placeholder': 'Favorite song', 'maxlength' : 80}, 
        validators=[validators.InputRequired(), validators.Length(max=80),
        validators.Regexp(r'^[\w]+$', message="Can only contain alphanumeric characters.")])
    movie = StringField('Favorite movie', render_kw={'placeholder': 'Favorite movie', 'maxlength' : 80}, 
        validators=[validators.InputRequired(), validators.Length(max=80),
        validators.Regexp(r'^[\w]+$', message="Can only contain alphanumeric characters.")])
    nationality = StringField('Nationality', render_kw={'placeholder': 'Your nationality', 'maxlength' : 80},
        validators=[validators.InputRequired(), validators.Length(max=80),
        validators.Regexp(r'^[\w]+$', message="Can only contain alphanumeric characters.")])
    birthday = DateField('Birthday')
    submit = SubmitField('Update Profile')
