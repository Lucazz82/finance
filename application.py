from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import requests 
import sqlite3
from helpers import login_required, is_float
from flask_sqlalchemy import SQLAlchemy

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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    hash = db.Column(db.String, nullable=False)


class Spending(db.Model):
    __tablename__ = 'spendings'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer)
    description = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String)
    instalments = db.Column(db.Integer)
    date = db.Column(db.DateTime)


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():

    if request.method == "POST":

        id = session['user_id'] 
        description = request.form.get('description')
        price = request.form.get('price')

        if not is_float(price):
            flash({'message': 'Invalid price', 'class': 'danger'}, 'message')
            return redirect(url_for('index'))

        price = float(price)

        category = request.form.get('category')
        instalments = request.form.get('instalments')
        n_instalments = request.form.get('number')

        if instalments == 'yes':
            if n_instalments.is_digit():
                n_instalments = int(n_instalments)
        else:
            n_instalments = 1

        spending = Spending(user_id=id, description=description, price=price, category=category, instalments=n_instalments)
        db.session.add(spending)
        db.session.commit()

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

        data = User.query.filter_by(username=username).first()

        if data is None:
            # invalid password or username
            flash({'message': 'Invalid username or password', 'class': 'danger'}, 'message')
            return redirect(url_for('login'))

        if not check_password_hash(data.hash, password):
            # invalid password or username
            flash({'message': 'Invalid username or password', 'class': 'danger'}, 'message')
            return redirect(url_for('login'))

        session['user_id'] = data.id
        flash({'message': f'{username} login successfully', 'class': 'success'}, 'message')
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
            flash({'message': "Must provide a username", 'class': 'danger'}, 'message')
            return redirect(url_for('register'))
        
        if not password:
            # need password
            flash({'message': 'Must provide a password', 'class': 'danger'}, 'message')
            return redirect(url_for('register'))

        if password != confirmation:
            flash({'message': "Password doesn't match", 'class': 'danger'}, 'message')
            return redirect(url_for('register'))
            
        if User.query.filter_by(username=username).count() != 0:
            flash({'message': 'Username already exists', 'class': 'danger'}, 'message')
            return redirect(url_for('register'))


        user = User(username=username, hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

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
