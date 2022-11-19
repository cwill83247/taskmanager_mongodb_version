import os                                   #std

from flask import (                         #std
    Flask, flash, render_template,
    redirect, request, session, url_for)                    

from flask_pymongo import PyMongo               #std
from bson.objectid import ObjectId              #std 
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):                #std
    import env


app = Flask(__name__)                   #std creating instance of Flask called app

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")   #std to get environmnet variables and use them 
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)      #std creating instalnce of PyMongo using the app defined above

@app.route("/")                         # std our inital home route ---- 
@app.route("/get_tasks")
def get_tasks():                            #function
    tasks = mongo.db.tasks.find()               # dont fully understand this syntax
    return render_template("tasks.html", tasks=tasks)   #dont fully understand this syntax 


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(                        #created a check and store it as existng_user
            {"username": request.form.get("username").lower()})

        if existing_user:                                               #if existing users is true    then flasjh a message
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {                                                            #variable being created called register that holds username nad password
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))    #generate_password_hash is the werkzeug helper function -----
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()              #session created 
        flash("Registration Successful!")
    return redirect(url_for("profile", username=session["user"]))               #setting username to session cookig of user !! bit unsure here 


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(                        #looking in the users table
            {"username": request.form.get("username").lower()})         # the value in table or field is username and its compairing value in form field using form name attribute

        if existing_user:                                          #if we have a users that matches go and check password otherwsie see bottom else staement 
            # ensure hashed password matches user input
            if check_password_hash(                                             #check_password_hash is a Werkzeug helper function that we can use as imported it 
                existing_user["password"], request.form.get("password")):   #if password matches login
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(
                        request.form.get("username")))
                    return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    
    if session["user"]:                                                 # adding a session variable check to stop a user being able to impersonate someone 
        return render_template("profile.html", username=username)       # if above is true then return prpfile otherwise return login
        
    return redirect(url_for("login")) 


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")                             #could also use session.clear 
    return redirect(url_for("login"))


if __name__ == "__main__":                              #std using this to test we can access env.py and values
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),          #std note converting Port to INT
            debug=True)                                 # !!In Live change to False