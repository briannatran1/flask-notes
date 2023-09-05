"""Flask app for Notes"""
import os

from models import db, connect_db, User
from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, session, flash, redirect
from flask_bcrypt import Bcrypt
from forms import RegisterForm, LoginForm, CSRFProtectForm

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
    form = CSRFProtectForm()

    return render_template('index.html',
                           form=form)


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Register form; handle registering user"""
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username=username,
                             password=password,
                             email=email,
                             first_name=first_name,
                             last_name=last_name)

        db.session.add(user)
        db.session.commit()

        session["username"] = user.username

        return redirect(f"/users/{username}")

    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username
            return redirect(f"/users/{username}")

        else:
            form.username.errors = ["Invalid Credentials"]

    return render_template("login.html", form=form)


@app.get("/users/<username>")
def display_user(username):
    """Displays user information"""
    user = User.query.get_or_404(username)

    if "username" not in session:
        flash("You must be logged in to view page")
        return redirect('/')
    else:
        return render_template("user_details.html",
                               user=user)


@app.post('/logout')
def logout():
    """Logs out user and redirects to register user"""
    form = CSRFProtectForm()

    if form.validate_on_submit():
        session.pop('username', None)

    return redirect('/')
