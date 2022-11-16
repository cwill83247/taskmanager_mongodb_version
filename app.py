import os                                   #std
from flask import Flask                     #std
if os.path.exists("env.py"):                #std
    import env


app = Flask(__name__)                   #std


@app.route("/")                         # std our inital home route ---- 
def hello():                            #function 
    return "Hello World ... again!"


if __name__ == "__main__":                              #std using this to test we can access env.py and values
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),          #std note converting Port to INT
            debug=True)                                 # !!In Live change to False