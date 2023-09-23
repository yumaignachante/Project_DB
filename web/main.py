
# Requirements Modules Open command prompt and download these below modules
# pip install flask
# pip install Flask-SQLAlchemy
# pip install Flask-Mail
# pip install mysqlclient
# pip install Flask-Login



from flask import Flask, json,redirect,render_template,flash,request
from flask.globals import request, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user


# mydatabase connection
local_server = True
app = Flask(__name__)
app.secret_key = "123"


# this is for getting the unique user access
login_manager=LoginManager(app)
login_manager.login_view='signin'

#connect to database
# ex. -> app.config['SQLALchemy_DATABASE_URI'] = 'mysql://username:password@localhost/databasename'
# ใช้ database ชื่ออะไรใน phpMyAdmin เช่นอันนี้ใข้dbชื่อ hospitalbedbooking
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/hospitalbedbooking'
db = SQLAlchemy(app)


with open('config.json','r') as c:
    params=json.load(c)["params"]


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

def load_beddata(bed_id):
    return Beds.query.get(str(bed_id))



class Test(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))

class Users(UserMixin,db.Model):
    user_id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(50), unique=True)
    password=db.Column(db.String(50))
    emp_id=db.Column(db.String(25), unique=True)

    def get_id(self):
        return str(self.user_id)
    

class Beds(db.Model):
    bed_id=db.Column(db.String(25),primary_key=True)
    room_id=db.Column(db.String(25))
    bed_type=db.Column(db.String(25))
    bed_status=db.Column(db.String(25))

    def get_id(self):
        return str(self.bed_id)


class Rooms(db.Model):
    room_id=db.Column(db.String(25),primary_key=True)
    room_name=db.Column(db.String(50))
    room_type=db.Column(db.String(25))
    dept_name=db.Column(db.String(255))




# -------------------------------------#
#               HOME PAGE
# -------------------------------------#





# หน้า Home page
@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        if request.form.get('action') == 'signin':
            print("เข้าLogin")
            username = request.form.get('username')
            password = request.form.get('password')
            user = Users.query.filter_by(username=username).first()
            
            if user:
                if user.password == password:
                    # ถ้าเข้าสู่ระบบสำเร็จให้ทำการลงชื่อเข้าใช้
                    login_user(user)
                    flash("Sign In สำเร็จ!")
                    # หลังจากลงชื่อเข้าใช้สามารถทำการ redirect ไปยังหน้าอื่นได้
                    return render_template('hometest.html')
                else:
                    flash("รหัสผ่านไม่ถูกต้อง!")
            else:
                flash("ไม่พบผู้ใช้!")




        elif request.form.get('action') == 'signup':
            print("เข้าRegist")
            emp_id = request.form.get('emp_id')
            username = request.form.get('username')
            password = request.form.get('password')
            print(emp_id, username, password)

            encpassword = generate_password_hash(password)

            # checkว่ากรอก emp_id กับ username ที่ใช้ไปแล้วรึเปล่า
            emp = Users.query.filter_by(emp_id=emp_id).first()
            user = Users.query.filter_by(username=username).first()
            if emp or user:
                flash("Already have this employee id or username", "warning")
            else:
                new_user = Users(emp_id=emp_id, username=username, password=password)
                db.session.add(new_user)
                db.session.commit()

                flash("Create user successfully! Please Sign In", "success")



            # ทำการบันทึกข้อมูลลงฐานข้อมูลหรือดำเนินการตามที่คุณต้องการที่นี่
    return render_template("hometest.html")




#หน้าAbout page
@app.route("/about", methods=['POST', 'GET'])

def about():

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        
        if user:
            if user.password == password:
                # ถ้าเข้าสู่ระบบสำเร็จให้ทำการลงชื่อเข้าใช้
                login_user(user)
                flash("Sign In สำเร็จ!")
                # หลังจากลงชื่อเข้าใช้สามารถทำการ redirect ไปยังหน้าอื่นได้
                return render_template('abouttest.html')
            else:
                flash("รหัสผ่านไม่ถูกต้อง!")
        else:
            flash("ไม่พบผู้ใช้!")


    return render_template("abouttest.html")


#หน้าdept Addmission
@app.route("/deptAddmission")

def deptAddmission():
    return render_template("deptAddmission.html")

#หน้าdept Heart
@app.route("/deptHeart")

def deptHeart():
    return render_template("deptHeart.html")

#หน้าdept Surgery
@app.route("/deptSurgery")

def deptSurgery():
    return render_template("deptSurgery.html")

#หน้าdept Medicine
@app.route("/deptMedicine")

def deptMedicine():
    return render_template("deptMedicine.html")

#หน้าdept Pediatrics
@app.route("/deptPediatrics")

def deptPediatrics():
    return render_template("deptPediatrics.html")

#หน้าdept Obstetrics
@app.route("/deptObstetrics")

def deptObstetrics():
    return render_template("deptObstetrics.html")

#หน้าdept Other
@app.route("/deptOther")

def deptOther():
    return render_template("deptOther.html")

# #หน้าSign Up
# @app.route("/signup")

# def signup():
#     return render_template("signup.html")


# #หน้าSign In
# @app.route("/signin")

# def signin():
#     return render_template("signin.html")






# -------------------------------------#
#               SIGN UP
# -------------------------------------#

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        emp_id = request.form.get('emp_id')
        username = request.form.get('username')
        password = request.form.get('password')
        print(emp_id, username, password)

        encpassword = generate_password_hash(password)

        # checkว่ากรอก emp_id กับ username ที่ใช้ไปแล้วรึเปล่า
        emp = Users.query.filter_by(emp_id=emp_id).first()
        user = Users.query.filter_by(username=username).first()
        if emp or user:
            flash("Already have this employee id or username", "warning")
        else:
            new_user = Users(emp_id=emp_id, username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            flash("Create user successfully! Please Sign In", "success")
            #return redirect('/signin')  # เปลี่ยนเป็นการ redirect ไปยังหน้า sign-in

    return render_template("hometest.html")




# -------------------------------------#
#               SIGN IN
# -------------------------------------#

@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(username=username).first()
        
        if user:
            if user.password == password:
                login_user(user)
                #flash("Sign In Successfully!", "info")
                return render_template("web.html")
                #return 'success'  # คืนค่า 'success' เมื่อการเข้าสู่ระบบประสบความสำเร็จ
            else:
                #return 'Incorrect password! the password is ' + user.password + ' you input ' + password
                flash("Incorrect password!", "danger")
        else:
            #return 'User not found!'
            flash("User not found!", "danger")

    return render_template("signin.html")


# -------------------------------------#
#               ADMIN LOGIN
# -------------------------------------#

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == "POST":
        username = request.form.get('adminuser')
        password = request.form.get('adminpassword')
        if(username==params['adminuser'] and password==params['adminpassword']):
            session['adminuser'] = username
            #flash("Login Successfully!", "info")
            return render_template("delBedpage.html")
            #return 'success'  # คืนค่า 'success' เมื่อการเข้าสู่ระบบประสบความสำเร็จ
        else:
            #return 'Incorrect password! the password is ' + user.password + ' you input ' + password
            flash("Incorrect password!", "danger")

    return render_template("adminlogin.html")



# -------------------------------------#
#              LOGOUT USER
# -------------------------------------#

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful!", "warning")
    return redirect(url_for('home'))

# -------------------------------------#
#              LOGOUT ADMIN
# -------------------------------------#

@app.route('/logoutadmin')
def logoutadmin():

    session.pop('adminuser')
    flash("Logout Admin Successful!", "primary")
    return redirect('/admin')

# -------------------------------------#
#              UPDATE BED
# -------------------------------------#

def updatess(code):
    postsdata = Beds.query.filter_by(bed_id=code).first()
    return render_template("addBedpage.html", postsdata=postsdata)


# -------------------------------------#
#              ADD BED PAGE
# -------------------------------------#
@app.route('/addBedpage', methods=['POST', 'GET'])
def addbed():



    if('adminuser' in session and session['adminuser']==params['adminuser']):
        if request.method=="POST":

            bed_id=request.form.get('bed_id')
            room_id=request.form.get('room_id')
            bed_type=request.form.get('bed_type')
            bed_status=request.form.get('bed_status')
            bedID=Beds.query.filter_by(bed_id=bed_id).first()
            roomID=Rooms.query.filter_by(room_id=room_id).first()

            #เช็กว่ามีbed_idนั้นแล้วในdbมั้ย ถ้ามี -> ไม่ให้add
            if bedID:
                flash("Bed ID is already Existed", "warning")
                return render_template("addBedpage.html")
            #เช็กว่ามีห้องในdbมั้ย ถ้ามี -> Add
            if not roomID:
                flash("Room ID doesn't Exist", "warning")
                return render_template("addBedpage.html")

            new_bed = Beds(bed_id=bed_id, room_id=room_id, bed_type=bed_type, bed_status=bed_status)
            db.session.add(new_bed)
            db.session.commit()
            flash("Bed Added!", "warning")
            return render_template("addBedpage.html")
            
    
    else:
        flash("Login and try Again", "warning")
        return redirect('/admin')
    
    return render_template("addBedpage.html")
    

# -------------------------------------#
#              DEL BED PAGE
# -------------------------------------#
@app.route('/delBedpage', methods=['POST', 'GET'])
def delbed():
    if('adminuser' in session and session['adminuser']==params['adminuser']):
        if request.method=="POST":

            bed_id=request.form.get('bed_id')
            room_id=request.form.get('room_id')
            bed_type=request.form.get('bed_type')
            bed_status=request.form.get('bed_status')
            bedID=Beds.query.filter_by(bed_id=bed_id).first()
            roomID=Rooms.query.filter_by(room_id=room_id).first()

            #เช็กว่ามีbed_idนั้นแล้วในdbมั้ย ถ้าไม่มี -> ไม่ลบ
            if not bedID:
                flash("Bed ID doesn't Exist", "warning")
                return render_template("delBedpage.html")
            
            # ลบเตียงจากฐานข้อมูล
            db.session.delete(bedID)
            db.session.commit()
            flash("Bed Deleted!", "warning")
            return render_template("delBedpage.html")
            
    
    else:
        flash("Login and try Again", "warning")
        return redirect('/admin')
    return render_template("delBedpage.html")



@app.route("/slotbooking")
@login_required
def slotbooking():
    return render_template("basebooking.html")



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