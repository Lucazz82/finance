from functools import wraps
from flask import session, redirect, url_for
import sqlite3

DATABASE = 'database.db'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def is_float(number);
    try:
        number = float(number)

    except:
        return False

    return True