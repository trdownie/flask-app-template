import os
from flask import (
    Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/index")
def index():
    films = mongo.db.films.find()
    return render_template("index.html", films=films)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # 1) CHECK WHETHER USERNAME EXISTS IN THE DB
        # a) define existing_user variable
        # b) get the (lowercase) username from the form
        # c) search 'users' collection to find first instance of username
        # d) if username found, assign it to existing_user
        # e) else existing_user undefined
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # 2) USERNAME ALREADY EXISTS
        # a) if existing_user = Truthy (has a value)
        if existing_user:
            # i) return error message
            flash(request.form.get("username")
                 + " already exists. Nice try, replicant.")
            # ii) redirect to registration page
            return redirect(url_for("register"))

        # 3) USERNAME DOESN'T EXIST
        else:
            # a) create a dictionary containing the user info
            register = {
                "username": request.form.get("username").lower(),
                "password": generate_password_hash(request.form.get("password"))
            }
            # b) insert the dictionary into the users collection
            mongo.db.users.insert_one(register)

            # c) add the newly created user into the session cookie
            session["member"] = request.form.get("username").lower()
            # d) display registration success message
            flash("Registration successful, "
                    + request.form.get("username") 
                    + ". Welcome, human.")
            # e) redirect the member to their member's area
            return redirect(url_for("members", member=session["member"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # 1) CHECK WHETHER USERNAME EXISTS (AS ABOVE)
        # (if found, existing_username is assigned user's document)
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # 2) USERNAME EXISTS - CHECK PASSWORD
        if existing_user:
            # a) hashed passwords match (input/db)
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        # i) set session variable 'member' to this username
                        session["member"] = request.form.get("username").lower()
                        # ii) send the member to their member's area
                        return redirect(url_for("members", member=session["member"]))
            # b) passwords don't match
            else:
                # i) return incorrect flash message
                flash("Username and/or password incorrect."
                         + " Thought Police dispatched.")                
                # ii) reload login page
                return redirect(url_for("login"))

        # 3) USERNAME DOESN'T EXIST
        else:
            # a) return incorrect flash message
            flash("Username and/or password incorrect."
                    + " Thought Police dispatched.")
            # b) reload login page
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/members/<member>", methods=["GET", "POST"])
def members(member):
    # 1) DEFINE THE MEMBER VARIABLE
    # a) take the session["member"] and find its instance in the db
    # b) since this will return doc, only return the ["username"] attribute
    member = mongo.db.users.find_one(
        {"username": session["member"]})["username"]
    # 2) RENDER MEMBERS TEMPLATE & PASSD IT MEMBER VARIABLE
    return render_template("members.html", member=member)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
