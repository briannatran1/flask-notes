"""Flask app for Notes"""
import os

from models import db, connect_db, User, Note
from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, session, flash, redirect
from flask_bcrypt import Bcrypt
from forms import RegisterForm, LoginForm, CSRFProtectForm, AddNoteForm, EditForm
from werkzeug.exceptions import Unauthorized

AUTH_KEY = 'username'

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

# make global constant for session var username


@app.get('/home')
def show_homepage():
    """Shows login and register options"""
    form = CSRFProtectForm()

    return render_template('index.html',
                           form=form)


@app.get('/')
def redirect_to_register():
    """Redirects back to register page"""

    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Register form; handle registering user"""
    # if user is in session, redirect to user profile

    if AUTH_KEY in session:
        return redirect(f"/users/{session[AUTH_KEY]}")

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
    # if user is in session, redirect to user profile
    if AUTH_KEY in session:
        return redirect(f'/users/{session[AUTH_KEY]}')

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session[AUTH_KEY] = user.username
            return redirect(f"/users/{username}")

        else:
            form.username.errors = ["Invalid Credentials"]

    return render_template("login.html", form=form)


@app.get("/users/<username>")
def display_user(username):
    """Displays user information and notes"""
    if AUTH_KEY not in session or username != session[AUTH_KEY]:
        flash("You must be logged in to view page")
        raise Unauthorized()

    user = User.query.get_or_404(username)
    notes = Note.query.all()

    return render_template("user_details.html",
                           user=user,
                           notes=notes)


@app.post('/logout')
def logout():
    """Logs out user and redirects to register user"""
    form = CSRFProtectForm()

    if form.validate_on_submit():
        session.pop(AUTH_KEY, None)
        return redirect('/login')

    return redirect('/home')


@app.post("/users/<username>/delete")
def delete_user(username):
    """Deletes user from database"""

    if AUTH_KEY not in session or username != session[AUTH_KEY]:
        raise Unauthorized()

    user = User.query.get_or_404(username)

    session.pop("username", None)

    db.session.delete(user)
    db.session.commit()

    return redirect("/login")


@app.route('/users/<username>/notes/add', methods=['GET', 'POST'])
def add_note(username):
    """Produce add note form or handle adding notes"""
    form = AddNoteForm()

    if AUTH_KEY not in session or username != session[AUTH_KEY]:
        raise Unauthorized()

    user = User.query.get_or_404(username)

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        note = Note(title=title,
                    content=content,
                    owner_username=username)

        db.session.add(note)
        db.session.commit()

        return redirect(f'/users/{username}')

    else:
        return render_template("add_note.html",
                               form=form,
                               user=user)


@app.route("/notes/<int:note_id>/update", methods=["GET", "POST"])
def edit_note(note_id):
    """Renders edit note form or handles edit notes"""
    note = Note.query.get_or_404(note_id)
    username = note.owner_username

    if AUTH_KEY not in session or username != session[AUTH_KEY]:
        raise Unauthorized()

    form = EditForm(obj=note)

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{note.owner_username}")

    return render_template("edit_note.html",
                           note=note,
                           form=form)


@app.post("/notes/<int:note_id>/delete")
def delete_note(note_id):
    """Deletes note from database"""
    note = Note.query.get_or_404(note_id)
    username = note.owner_username

    if AUTH_KEY not in session or username != session[AUTH_KEY]:
        raise Unauthorized()

    if username == session[AUTH_KEY]:
        db.session.delete(note)
        db.session.commit()

    return redirect(f"/users/{note.owner_username}")
