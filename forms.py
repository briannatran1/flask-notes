"""Forms for note app."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email


class RegisterForm(FlaskForm):
    """Form for registering to site"""

    username = StringField('Username',
                           validators=[InputRequired()])
    password = PasswordField('Password',
                             validators=[InputRequired()])
    email = StringField('Email Address',
                        validators=[InputRequired(), Email()])
    first_name = StringField('First Name',
                             validators=[InputRequired()])
    last_name = StringField('Last Name',
                            validators=[InputRequired()])


class LoginForm(FlaskForm):
    """Form for logging to site"""

    username = StringField('Username',
                           validators=[InputRequired()])
    password = PasswordField('Password',
                             validators=[InputRequired()])
