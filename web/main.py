
# Requirements Modules Open command prompt and download these below modules
# pip install flask
# pip install Flask-SQLAlchemy
# pip install Flask-Mail
# pip install mysqlclient
# pip install Flask-Login

# some pc use
# py -m pip install flask



#-----------------------------------------------------------------------------------------------------------------
# ***** ในการเข้า Admin session ต้องสมัคร/เข้าสู่ระบบด้วย username กับ password เดียวกับที่ตั้งไว้ในไฟล์ config.json เท่านั้น ******
#               username : admin 
#               password : admin123
#-----------------------------------------------------------------------------------------------------------------



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



# ดึงข้อมูลจาก table Users
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# ดึงข้อมูลจาก table Beds
def load_beddata(bed_id):
    return Beds.query.get(str(bed_id))




# -----------------------------------------------#
#              class Table จาก DB
# -----------------------------------------------#


class Test(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))

class Users(UserMixin,db.Model):
    user_id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(50), unique=True)
    password=db.Column(db.String(50))
    emp_id=db.Column(db.Integer, unique=True)

    def get_id(self):
        return str(self.user_id)
    

class Beds(db.Model):
    bed_id=db.Column(db.String(25),primary_key=True)
    room_id=db.Column(db.String(25))
    bed_type=db.Column(db.String(25))
    bed_status=db.Column(db.String(25))
    dept_name=db.Column(db.String(255))

    def get_id(self):
        return str(self.bed_id)


class Rooms(db.Model):
    room_id=db.Column(db.String(25),primary_key=True)
    room_name=db.Column(db.String(50))
    room_type=db.Column(db.String(25))
    dept_name=db.Column(db.String(255))

class Departments(db.Model):
    dept_id=db.Column(db.Integer,primary_key=True)
    dept_name=db.Column(db.String(255))
    dept_location=db.Column(db.String(255))
    dept_floor=db.Column(db.String(50))

class Employees(UserMixin, db.Model):
    emp_id=db.Column(db.Integer, primary_key=True)
    # emp_fname=db.Column(db.String(50))
    # emp_lname=db.Column(db.String(50))
    # dept_id=db.Column(db.Integer)
    # job_id=db.Column(db.String(25))
    # emp_phone=db.Column(db.String(12))
    
    def get_id(self):
        return int(self.emp_id)





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
                    # return render_template('hometest.html')
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

            # check emp_id ใน employees มีจริง
            emp_in_emps = Employees.query.filter_by(emp_id=emp_id).first()
            if emp or user:
                flash("หมายเลขหรือชื่อผู้ใช้นี้ถูกใช้งานไปแล้ว", "warning")
                # flash("Already have this employee id or username", "warning")
            
            elif not emp_in_emps:
                flash("ไม่พบหมายเลขใบอนุญาตทางการแพทย์นี้", "warning")
            else:
                new_user = Users(emp_id=emp_id, username=username, password=password)
                db.session.add(new_user)
                db.session.commit()

                flash("สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ!", "success")
                # flash("Create user successfully! Please Sign In", "success")



            # ทำการบันทึกข้อมูลลงฐานข้อมูลหรือดำเนินการตามที่คุณต้องการที่นี่
    return render_template("hometest.html")




#หน้าAbout page
@app.route("/about", methods=['POST', 'GET'])

def about():

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
                    # return render_template('hometest.html')
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

            # check emp_id ใน employees มีจริง
            emp_in_emps = Employees.query.filter_by(emp_id=emp_id).first()
            if emp or user:
                flash("หมายเลขหรือชื่อผู้ใช้นี้ถูกใช้งานไปแล้ว", "warning")
                # flash("Already have this employee id or username", "warning")
            
            elif not emp_in_emps:
                flash("ไม่พบหมายเลขใบอนุญาตทางการแพทย์นี้", "warning")
            else:
                new_user = Users(emp_id=emp_id, username=username, password=password)
                db.session.add(new_user)
                db.session.commit()

                flash("สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ!", "success")
                # flash("Create user successfully! Please Sign In", "success")



            # ทำการบันทึกข้อมูลลงฐานข้อมูลหรือดำเนินการตามที่คุณต้องการที่นี่
    return render_template("abouttest.html")


#หน้า bed booking
@app.route("/bedbooking")

def bedbooking():
    return render_template("bedbooking.php")

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
#               OLD SIGN UP
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
#               OLD SIGN IN
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
                return render_template("hometest.html")
                #return 'success'  # คืนค่า 'success' เมื่อการเข้าสู่ระบบประสบความสำเร็จ
            else:
                #return 'Incorrect password! the password is ' + user.password + ' you input ' + password
                flash("Incorrect password!", "danger")
        else:
            #return 'User not found!'
            flash("User not found!", "danger")

    return render_template("hometest.html")


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


            user = Users.query.filter_by(username=username).first()
            login_user(user)
            #flash("Login Successfully!", "info")
            return render_template("adminlognew.html")
            #return 'success'  # คืนค่า 'success' เมื่อการเข้าสู่ระบบประสบความสำเร็จ
        else:
            #return 'Incorrect password! the password is ' + user.password + ' you input ' + password
            flash("Incorrect password!", "danger")

    return render_template("adminlognew.html")



    # if request.method == "POST":
    #     username = request.form.get('adminuser')
    #     password = request.form.get('adminpassword')
    #     if(username==params['adminuser'] and password==params['adminpassword']):
    #         session['adminuser'] = username
    #         #flash("Login Successfully!", "info")
    #         return render_template("delBedpage.html")
    #         #return 'success'  # คืนค่า 'success' เมื่อการเข้าสู่ระบบประสบความสำเร็จ
    #     else:
    #         #return 'Incorrect password! the password is ' + user.password + ' you input ' + password
    #         flash("Incorrect password!", "danger")

    # return render_template("adminlogin.html")



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

    logout_user()
    # session.pop('adminuser')
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


    # check ว่าเป็น admin login อยู่ในระบบ อยู่ป่าว
    if('adminuser' in session and session['adminuser']==params['adminuser']):
        if request.method=="POST":

            bed_id=request.form.get('bed_id')
            room_id=request.form.get('room_id')
            bed_type=request.form.get('bed_type')
            bed_status=request.form.get('bed_status')
            dept_name=request.form.get('dept_name')

            
            bedID=Beds.query.filter_by(bed_id=bed_id).first()
            roomID=Rooms.query.filter_by(room_id=room_id).first()
            deptName=Departments.query.filter_by(dept_name=dept_name).first()

            #เช็กว่ามีbed_idนั้นแล้วในdbมั้ย ถ้ามี -> ไม่ให้add
            if bedID:
                flash("Bed ID is already Existed", "warning")
                return render_template("addBedpage.html")
            #เช็กว่ามีห้องในdbมั้ย ถ้ามี -> Add
            if not roomID:
                flash("Room ID doesn't Exist", "warning")
                return render_template("addBedpage.html")
            
            #เช็กว่ามี แผนก ในdbมั้ย ถ้ามี -> Add
            if not deptName:
                flash("Department doesn't Exist", "warning")
                return render_template("addBedpage.html")
            

            new_bed = Beds(bed_id=bed_id, room_id=room_id, bed_type=bed_type, bed_status=bed_status, dept_name=dept_name)
            db.session.add(new_bed)
            db.session.commit()
            flash("Bed Added!", "warning")
            return render_template("addBedpage.html")
            
    

    # ไม่ใช่ admin login อยู่ ไม่ให้เข้าหน้า addBedpage
    else:
        flash("Login and try Again", "warning")
        return redirect('/admin')
    
    return render_template("addBedpage.html")
    

# -------------------------------------#
#              DEL BED PAGE
# -------------------------------------#
@app.route('/delBedpage', methods=['POST', 'GET'])
def delbed():

    # check ว่าเป็น admin login อยู่ในระบบ อยู่ป่าว
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
            
    # ไม่ใช่ admin login อยู่ ไม่ให้เข้าหน้า addBedpage
    else:
        flash("Login and try Again", "warning")
        return redirect('/admin')
    return render_template("delBedpage.html")




# -------------------------------------#
#              SLOT BED PAGE
# -------------------------------------#

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