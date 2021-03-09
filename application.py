from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import requests 
import sqlite3
from helpers import login_required

# Configure application
app = Flask(__name__)

# Autoreload template
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
db = sqlite3.connect("database.db")
db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, username TEXT NOT NULL, hash TEXT NOT NULL, PRIMARY KEY(id))')


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():

    if request.method == "POST":
        session['name'] = request.form.get('name')
        return redirect(url_for('index'))

    name = ""
    if 'name' in session:
        name = session['name']

    return render_template('index.html', name=name)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username:
            # need username
            flash('Must provide a username', 'danger')
            return redirect(url_for('login'))

        if not password:
            # need password
            flash('Must provide a password', 'danger')
            return redirect(url_for('login'))

        data = []

        for row in db.execute('select hash, id from users where username = ?', (username,)):
            data.append(row)

        if len(data) != 1:
            # invalid password or username
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

        if not check_password_hash(data[0][0], password):
            # invalid password or username
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

        session['user_id'] = data[0][1]
        flash(f'{username} login successfully', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        if not username:
            # need username
            flash("Must provide a username", 'danger')
            return redirect(url_for('register'))
        
        if not password:
            # need password
            flash('Must provide a password', 'danger')
            return redirect(url_for('register'))

        if password != confirmation:
            flash("Password doesn't match", 'danger')
            return redirect(url_for('register'))

        data = (username, generate_password_hash(password))

        db.execute('INSERT INTO users (username, hash) VALUES (?, ?)', data)
        db.commit()        

        return redirect(url_for('login'))

    return render_template('register.html')


def error(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template('error.html', code=e.code, name=e.name)

for code in default_exceptions:
    app.errorhandler(code)(error)
    