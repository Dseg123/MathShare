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
import json

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

def queryDB(query, vals = ()):
    myConn = create_connection(r"/mnt/c/Users/aepst/Documents/Projects/Project1/proj1.db")
    myConn.row_factory = sqlite3.Row
    cur = myConn.cursor()
    cur.execute(query, vals)
    myConn.commit()
    answer = cur.fetchall()
    myConn.close()
    return answer

# def fillPosts():
#     letters = string.ascii_letters
#     for i in range(100):
#         myId = random.choice([3, 4])
#         myTitle = ''.join([random.choice(letters) for j in range(10)])
#         myBody = ''.join([random.choice(letters) for j in range(100)])
#         myCategory = random.choice(["Story", "Funny", "Serious", "Hot Take", "Advice", "Question"])
#         myTimestamp = datetime.now()
#         cur.execute("INSERT INTO posts (posterID, title, body, category, timestamp) VALUES (?, ?, ?, ?, ?)", (myId, myTitle, myBody, myCategory, myTimestamp))
#         myConn.commit()
# fillPosts()

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
    #print(myId)
    rows = queryDB("SELECT username FROM users WHERE id = ?", (myId,))
    if len(rows) == 0:
        return redirect("/login")
    #print(rows)
    #print(dict(rows[0]))
    uname = dict(rows[0])['username']
    #print(dict(rows[0]))
    return render_template('index.html', myName = uname)


@app.route("/signup", methods = ["GET", "POST"])
def signup():
    #print("HI")
    if request.method == "POST":
        #print(request.form)
        myUsername = request.form.get("username")
        myPassword = request.form.get("password")
        myConf = request.form.get("confirmation")
        pastNames = queryDB("SELECT username FROM users")
        #print(pastNames)
        msg = helpers.checkReg(myUsername, myPassword, myConf, pastNames)
        if msg != "Good":
            return render_template("signup.html", errMsg = msg)
        else:
            myHash = generate_password_hash(myPassword)
            wueryDB("INSERT INTO users (username, hash) VALUES (?, ?)", (myUsername, myHash))
            return redirect("/")
    else:
        return render_template("signup.html", errMsg = None)
    

@app.route("/login", methods = ["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        myName = request.form.get("username")
        myPword = request.form.get("password")
        #print(myName, myPword)
        if myName is None or len(myName) == 0 or myPword is None or len(myPword) == 0:
            return render_template("login.html", errMsg = "Please complete all sections")
        rows = queryDB("SELECT * FROM users WHERE username = ?", (myName,))
        rows = [dict(x) for x in rows]
        #print(rows)
        if len(rows) != 1 or not check_password_hash(rows[0]['hash'], myPword):
            return render_template("login.html", errMsg = "Invalid username and/or password")
        
        session["user_id"] = rows[0]['id']
        return redirect("/")
    else:
        return render_template("login.html", errMsg = None)

@app.route("/posts", methods = ["GET", "POST"])
def posts():
    print("GOTTEENNN")
    if request.method == "GET":
        print("GOTTEN")
        rows = queryDB("SELECT * FROM posts")
        rows = [dict(x) for x in rows]
        for row in rows:
            posterId = row['posterID']
            #print("posterID", posterId)
            answer = queryDB("SELECT username FROM users where id = ?", (posterId,))
            answer = dict(answer[0])['username']
            row['poster'] = answer
        myData = rows[:min(len(rows), 25)]
        #print(myData)
        return render_template("posts.html", data = myData)
    else:
        print(request.form.get("poster"))
        p = request.form.get("poster")
        rows = []
        if p == "":
            rows = queryDB("SELECT * FROM posts")
        else: 
            answer = queryDB("SELECT id FROM users WHERE username = ?", (p,))
            posterId = 0
            if len(answer) == 0:
                print("None found")
                return json.dumps([])
            else:
                posterId = dict(answer[0])["id"]
            print(posterId)
            rows = queryDB("SELECT * FROM posts WHERE posterId = ?", (posterId,))
        rows = [dict(x) for x in rows]
        for row in rows:
            posterId = row['posterID']
            #print("posterID", posterId)
            answer = queryDB("SELECT username FROM users where id = ?", (posterId,))
            answer = dict(answer[0])['username']
            row['poster'] = answer
        myData = rows
        print("almostdone")
        print(myData)
        print(json.dumps(myData))
        print(type(json.dumps(myData)))
        print("YOOOOOOOOO")
        return json.dumps(myData)

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