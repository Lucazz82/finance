from flask import Flask, render_template, session, redirect, url_for, request
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
import requests 

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

@app.route('/', methods=['GET', 'POST'])
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
    return render_template('login.html')

def error(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template('error.html', code=e.code, name=e.name)

for code in default_exceptions:
    app.errorhandler(code)(error)
    