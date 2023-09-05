"""Flask app for Notes"""
import os

from models import db, connect_db, User
from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, request, render_template
from flask_bcrypt import Bcrypt
from forms import RegisterForm, LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = "secret"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", "postgresql:///users")

connect_db(app)

bcrypt = Bcrypt()

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)


@app.get('/')
def redirect_to_register():
    """Redirects back to register page"""

    return render_template('register.html')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Register form; handle registering user"""
    form = RegisterForm()

    if form.validate_on_submit():

