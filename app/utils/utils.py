from datetime import datetime, timedelta, timezone
from flask import session


def set_session_expiry():
    session['expiry'] = datetime.utcnow() + timedelta(minutes=30)


def is_session_valid():
    expiry = session.get('expiry')
    if expiry and expiry.replace(tzinfo=timezone.utc) > datetime.utcnow().replace(tzinfo=timezone.utc):
        return True
    else:
        session.clear()
        return False