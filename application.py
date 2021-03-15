from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import requests 
import sqlite3
from helpers import login_required, Database

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
# db = sqlite3.connect("database.db")
# execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, username TEXT NOT NULL, hash TEXT NOT NULL, PRIMARY KEY(id))')
# execute('CREATE TABLE IF NOT EXISTS expense (id INTEGER NOT NULL, description TEXT NOT NULL, price REAL NOT NULL, category TEXT, instalments INTEGER)')

db = Database('database.db')


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():

    if request.method == "POST":

        id = session['user_id'] 
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')
        instalments = request.form.get('instalments')
        n_instalments = request.form.get('number')

        if instalments == 'yes':
            if n_instalments.is_digit():
                n_instalments = int(n_instalments)
        else:
            n_instalments = 1

        # cur = db.cursor()
        # cur.execute('INSERT INTO expense (id, description, price, category, instalments) VALUES (?,?,?,?,?)', (id, description, price, category, n_instalments))
        # db.commit()
        db.execute('INSERT INTO expense (id, description, price, category, instalments) VALUES (?,?,?,?,?)', (id, description, price, category, n_instalments))
        return redirect(url_for('index'))

    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username:
            # need username
            flash({'message': 'Must provide a username', 'class': 'danger'}, 'message')
            return redirect(url_for('login'))

        if not password:
            # need password
            flash({'message': 'Must provide a password', 'class': 'danger'}, 'message')
            flash(username, 'username')       
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


@app.route('/spendingCategories')
@login_required
def spendingCategories():
    # select all the categories for the user and return
    id = session['user_id']
    data = db.execute('SELECT category FROM expense WHERE id=? GROUP BY category', {id,})
    return data


def error(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template('error.html', code=e.code, name=e.name)

for code in default_exceptions:
    app.errorhandler(code)(error)
