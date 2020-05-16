from flask import Flask
from flask import render_template, render_template_string, flash, session, request, redirect
from subprocess import PIPE
import bcrypt
import sqlite3

app = Flask(__name__)

db = sqlite3.connect('database.db', check_same_thread=False)
initCursor = db.cursor()

initCursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
if len(initCursor.fetchall()) != 1:
    initCursor.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL);")
    initCursor.execute(
        "CREATE TABLE posts (id INTEGER PRIMARY KEY AUTOINCREMENT, userId INTEGER NOT NULL, content TEXT NOT NULL);")
    initCursor.execute(
        "INSERT INTO users (username, password) VALUES ('admin', '');")
    db.commit()

initCursor.close()

app.secret_key = b'\xce\x11s\xbcZ\xc1\xa4\x08\x1fX\xf5A!\xa1\xe68'


# We have to use our own thing to allow the users to format their messages with html
def templateAsString(template):
    with open('templates/{}'.format(template), 'r') as file:
        data = file.read().replace('\n', '')
        return data


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login')
def login():
    if "id" in session:
        return redirect("/home")
    else:
        return render_template('login.html')


@app.route('/signup')
def signup():
    if "id" in session:
        return redirect("/home")
    else:
        return render_template('signup.html')


@app.route('/signout')
def signout():
    if "id" in session:
        session.pop("id", None)
    return redirect("/")


@app.route('/login', methods=['POST'])
def do_login():
    if len(request.form['password']) == 0 or len(request.form['username']) == 0:
        flash("You must enter a username and password.")
        return login()
    else:
        c = db.cursor()
        c.execute("SELECT id, password FROM users WHERE username = ?", [
                  request.form['username']])
        row = c.fetchone()
        c.close()
        if(row == None):
            flash("Invalid login")
            return login()
        elif (bcrypt.checkpw(str.encode(request.form['password']), row[1])):
            session['id'] = row[0]
            return redirect("/home")
        else:
            flash("Invalid login")
            return login()


@app.route('/signup', methods=['POST'])
def do_signup():
    if len(request.form['password']) == 0 or len(request.form['username']) == 0:
        flash("You must enter a username and password.")
    else:
        username = request.form['username']
        password = request.form['password']
        c = db.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", [username])
        if len(c.fetchall()) != 0:
            flash("That username has already been used.")
        else:
            hashedPassword = bcrypt.hashpw(
                str.encode(password), bcrypt.gensalt())
            c.execute("INSERT INTO USERS (username, password) VALUES (?, ?);",
                      [username, hashedPassword])
            db.commit()
            c.close()
            flash("You've signed up, now log in.")
            return redirect("/login")
        c.close()
    return signup()


@app.route('/placeOrder', methods=['POST'])
def do_place_order():
    if not "id" in session:
        flash("You have to login to access that page.")
        return login()
    elif len(request.form["content"]) == 0:
        return "You must enter some content."
    else:
        c = db.cursor()
        c.execute("INSERT INTO posts (userId, content) VALUES (?, ?)", [
                  session["id"], request.form["content"]])
        db.commit()

        return redirect("/home")


@app.route("/home")
def home():
    if not "id" in session:
        flash("You have to login to access that page.")
        return login()
    else:
        c = db.cursor()
        c.execute("SELECT content FROM posts WHERE userId = ? ORDER BY id DESC", [
                  session["id"]])
        latestOrderRow = c.fetchone()
        latestOrder = "You haven't placed any orders"
        if latestOrderRow != None:
            latestOrder = latestOrderRow[0]

        return render_template_string(templateAsString("home.html").replace("<!--temp:LatestOrder-->", latestOrder))


@app.route('/admin')
def admin():
    if not "id" in session:
        flash("You must be logged in to reach that page.")
        return redirect("/login")
    elif session["id"] == 1:
        flash("hackDalton{4dm1n_1s_numb3r_0n3_TIfIZBTBu_}")
    else:
        flash("You aren't an admin")
    return redirect("/home")


@app.errorhandler(500)
def internal_server_error(error):
    return "An internal server error occured. Broke a user? Go to /signout to sign out and sign in as a different user."


if __name__ == "__main__":
    app.run()
