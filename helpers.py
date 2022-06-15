import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("user id?", session.get("user_id"))
        if session.get("user_id") is None:
            return redirect("/login")
        
        return f(*args, **kwargs)
    return decorated_function

def checkReg(username, password, conf, pastNames):
    if username is None or len(username) == 0 or password is None or len(password) == 0 or conf is None or len(conf) == 0:
        return "Please fill out all sections"
    if " " in username or " " in password or " " in conf:
        return "Do not include spaces in username or password"
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if password != conf:
        return "Confirmation does not match password"
    print([dict(row) for row in pastNames])
    if username in [dict(row)['username'] for row in pastNames]:
        return "Username already used"
    return "Good"    
    
