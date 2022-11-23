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
    tasks = list(mongo.db.tasks.find())            # dont fully understand this syntax
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
    
    return render_template("register.html")

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


@app.route("/add_task", methods=["GET", "POST"])        # DOnt forget to Add the Methods !!!!
def add_task():
    if request.method == "POST":                                     #checking if POST method
        is_urgent = "on" if request.form.get("is_urgent") else "off"  #creating a variable to hold the is urgent on or off
        task = {                                                       #creating a dictonairy with variable name "task" to hold the values in value pairs from the form         
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"),
            "is_urgent": is_urgent,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]                       # adding users session so that we have a record of who created it --- 
        }
        mongo.db.tasks.insert_one(task)                             # inserting task variable into the DB
        flash("Task Successfully Added")                            # message to user
        return redirect(url_for("get_tasks"))                       # then going back  to the get_tasks function but is actually tasks.html 

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_task.html", categories=categories)


@app.route("/edit_task/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        submit = { "$set": {
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"),
            "is_urgent": is_urgent,
            "due_date": request.form.get("due_date"),
            #"created_by": session["user"]
        }}
        mongo.db.tasks.update_one({"_id": ObjectId(task_id)}, submit)
        flash("Task Successfully Updated")

    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_task.html", task=task, categories=categories)


@app.route("/delete_task/<task_id>")
def delete_task(task_id):
    mongo.db.tasks.delete_one({"_id": ObjectId(task_id)})
    flash("Task Successfully Deleted")
    return redirect(url_for("get_tasks"))

@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1)) # we are also sorting the list alphbetically
    return render_template("categories.html", categories=categories)  #categories=categories  1st category is what actually gets passed to categories.html the 2nd is the varibale we create above


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = { "$set": {
            "category_name": request.form.get("category_name")
        }}
        mongo.db.categories.update_one({"_id": ObjectId(category_id)}, submit)
        flash("Category Successfully Updated")
        return redirect(url_for("get_categories"))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)



if __name__ == "__main__":                              #std using this to test we can access env.py and values
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),          #std note converting Port to an INT
            debug=True)                                 # !!In Live change to False