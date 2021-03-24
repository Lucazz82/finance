from functools import wraps
from flask import session, redirect, url_for, flash
import sqlite3
from datetime import datetime
# from dateutil import tz
from dateutil import tz
DATABASE = 'database.db'

# Config timezone
utc_timezone = tz.tzutc()
local_timezone = tz.tzlocal()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def is_float(number):
    try:
        number = float(number)

    except:
        return False

    return True


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def instalments(value):
    n_instalments = value.instalments

    if n_instalments == 1:
        return "No"

    month = int(value.date.strftime('%m'))
    current_month = int(datetime.now().strftime('%m'))
    paid = current_month - month

    if paid > n_instalments:
        return f"{n_instalments}/{n_instalments}"

    return f"{paid}/{n_instalments}"


def utc_to_local(time):
    return time.replace(tzinfo=utc_timezone).astimezone(tz=local_timezone)


# Conver the time from UTC (which is stored in db) to current timezone
def date(value):
    time = utc_to_local(value)
    return time.strftime('%d/%m')