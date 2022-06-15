import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from datetime import datetime
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
import sqlite3
from sqlite3 import Error
import helpers
import string
import random

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except Error as e:
        print(e)

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

myConn = create_connection(r"/mnt/c/Users/aepst/Documents/Projects/Project1/proj1.db")
myConn.row_factory = sqlite3.Row
cur = myConn.cursor()


def fillPosts():
    letters = string.ascii_letters
    for i in range(100):
        myId = random.choice([3, 4])
        myTitle = ''.join([random.choice(letters) for j in range(10)])
        myBody = ''.join([random.choice(letters) for j in range(100)])
        myCategory = random.choice(["Story", "Funny", "Serious", "Hot Take", "Advice", "Question"])
        myTimestamp = datetime.now()
        cur.execute("INSERT INTO posts (posterID, title, body, category, timestamp) VALUES (?, ?, ?, ?, ?)", (myId, myTitle, myBody, myCategory, myTimestamp))
        myConn.commit()
fillPosts()

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@helpers.login_required
def index():
    myId = session.get("user_id")
    print(myId)
    cur.execute("SELECT username FROM users WHERE id = ?", (myId,))
    rows = cur.fetchall()
    if len(rows) == 0:
        return redirect("/login")
    print(rows)
    #print(dict(rows[0]))
    uname = dict(rows[0])['username']
    print(dict(rows[0]))
    return render_template('index.html', myName = uname)


@app.route("/signup", methods = ["GET", "POST"])
def signup():
    print("HI")
    if request.method == "POST":
        print(request.form)
        myUsername = request.form.get("username")
        myPassword = request.form.get("password")
        myConf = request.form.get("confirmation")
        cur.execute("SELECT username FROM users")
        pastNames = cur.fetchall()
        print(pastNames)
        msg = helpers.checkReg(myUsername, myPassword, myConf, pastNames)
        if msg != "Good":
            return render_template("signup.html", errMsg = msg)
        else:
            myHash = generate_password_hash(myPassword)
            cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (myUsername, myHash))
            myConn.commit()
            return redirect("/")
    else:
        return render_template("signup.html", errMsg = None)
    

@app.route("/login", methods = ["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        myName = request.form.get("username")
        myPword = request.form.get("password")
        print(myName, myPword)
        if myName is None or len(myName) == 0 or myPword is None or len(myPword) == 0:
            return render_template("login.html", errMsg = "Please complete all sections")
        cur.execute("SELECT * FROM users WHERE username = ?", (myName,))
        rows = [dict(x) for x in cur.fetchall()]
        print(rows)
        if len(rows) != 1 or not check_password_hash(rows[0]['hash'], myPword):
            return render_template("login.html", errMsg = "Invalid username and/or password")
        
        session["user_id"] = rows[0]['id']
        return redirect("/")
    else:
        return render_template("login.html", errMsg = None)

@app.route("/posts")
def posts():
    return render_template("posts.html")

@app.route("/write")
def write():
    return render_template("write.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")