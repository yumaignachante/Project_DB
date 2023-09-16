from flask import Flask, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


# mydatabase connection
local_server = True
app = Flask(__name__)
app.secret_key = "123"


#connect to database
# ex. -> app.config['SQLALchemy_DATABASE_URI'] = 'mysql://username:password@localhost/databasename'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/hospitalbedbooking'
db = SQLAlchemy(app)


class Test(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))


#หน้าHome page
@app.route("/")

def home():
    return render_template("web.html")


#หน้าSign In
@app.route("/signin")

def signin():
    return render_template("signin.html")

#check test db is connect or not
#ใส่/testหลังURL
@app.route("/test")

def test():
    try:
        a=Test.query.all()
        print(a)
        return f'MY DATABASE IS CONNECTED'
    except Exception as e:
        print(e)
        return f'DATABASE IS NOT CONNECTED {e}'



app.run(debug=True)