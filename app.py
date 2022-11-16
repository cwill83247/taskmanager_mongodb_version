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
    return render_template("register.html")


if __name__ == "__main__":                              #std using this to test we can access env.py and values
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),          #std note converting Port to INT
            debug=True)                                 # !!In Live change to False