
# Requirements Modules Open command prompt and download these below modules
# pip install flask
# pip install Flask-SQLAlchemy
# pip install Flask-Mail
# pip install mysqlclient
# pip install Flask-Login
# pip install Flask-WTF

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

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from flask import Flask, render_template, flash, redirect, url_for, make_response
from sqlalchemy.orm import join
from sqlalchemy import func

from datetime import datetime


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

def load_roomdata(room_id):
    return Rooms.query.get(str(room_id))

def load_deptdata(dept_id):
    return Departments.query.get(int(dept_id))

def load_bookingdata(bk_id):
    return Booking.query.get(int(bk_id))

def load_patientdata(pt_ssn):
    return Patients.query.get(str(pt_ssn))

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
    def get_id(self):
        return str(self.room_id)

class Departments(db.Model):
    dept_id=db.Column(db.Integer,primary_key=True)
    dept_name=db.Column(db.String(255))
    dept_location=db.Column(db.String(255))
    dept_floor=db.Column(db.String(50))
    def get_id(self):
        return str(self.dept_id)
    
class Employees(UserMixin, db.Model):
    emp_id=db.Column(db.Integer, primary_key=True)
    # emp_fname=db.Column(db.String(50))
    # emp_lname=db.Column(db.String(50))
    # dept_id=db.Column(db.Integer)
    # job_id=db.Column(db.String(25))
    # emp_phone=db.Column(db.String(12))
    
    def get_id(self):
        return int(self.emp_id)

class Booking(db.Model):
    bk_id = db.Column(db.Integer, primary_key = True)
    pt_ssn = db.Column(db.String(13))
    bed_id = db.Column(db.String(25))
    room_id = db.Column(db.String(25))
    dept_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    bk_ad_time = db.Column(db.DateTime, default=datetime.utcnow)  # เวลาที่สร้างรายการ
    bk_update_time = db.Column(db.DateTime, onupdate=datetime.utcnow)  # เวลาที่อัปเดตรายการ
    bk_status = db.Column(db.String(25))

    def get_id(self):
        return int(self.bk_id)

class Patients(db.Model):
    pt_ssn = db.Column(db.String(13), primary_key = True)
    pt_fname = db.Column(db.String(50))
    pt_lname = db.Column(db.String(50))
    pt_dob = db.Column(db.Date())
    pt_age = db.Column(db.Integer)
    pt_gender = db.Column(db.String(25))
    pt_adn = db.Column(db.String(11))
    pt_phone_number = db.Column(db.String(12))
    trauma_id = db.Column(db.String(25))

    def get_id(self):
        return int(self.pt_ssn)



# เพิ่มส่วนของการสร้างแบบฟอร์มสำหรับการเพิ่มข้อมูลเตียง
class InsertForm(FlaskForm):
    bed_id = StringField('Bed ID', validators=[DataRequired()])
    room_id = StringField('Room ID', validators=[DataRequired()])
    bed_type = StringField('Bed Type', validators=[DataRequired()])
    bed_status = StringField('Bed Status', validators=[DataRequired()])
    dept_name = StringField('Department Name', validators=[DataRequired()])
    submit = SubmitField('Add Bed')



# -------------------------------------#
#               HOME PAGE
# -------------------------------------#


# หน้า Home page
@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if(username==params['adminuser'] and password==params['adminpassword']):
            session['adminuser'] = username


            user = Users.query.filter_by(username=username).first()
            login_user(user)
            return render_template('adminlognew.html')

        elif request.form.get('action') == 'signin':
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
        username = request.form.get('username')
        password = request.form.get('password')
        if(username==params['adminuser'] and password==params['adminpassword']):
            session['adminuser'] = username


            user = Users.query.filter_by(username=username).first()
            login_user(user)
            return render_template('adminlognew.html')

        elif request.form.get('action') == 'signin':
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

        # ดึงข้อมูลที่ผู้ใช้เลือกในฟอร์ม
        selected_room_type = request.args.get('room_id')
        selected_bed_type = request.args.get('bed_type')
        selected_dept_name = request.args.get('dept_name')
        selected_bed_status = request.args.get('bed_status')

        # อัปเดต query ในการดึงข้อมูล ใช้ join เพื่อเชื่อมข้อมูล 2 ตารางเข้ามาเพื่อใช้ในการค้นหาข้อมูลจากทั้ง2ตาราง
        beds_data = Beds.query.join(Rooms, Beds.room_id == Rooms.room_id)


        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        if selected_room_type and selected_room_type != 'Select Room Type':
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            print(f'Selected Bed Status: {selected_bed_status}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_status == selected_bed_status)


        # นับจำนวนข้อมูล ของ beds_data
        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        beds_data = beds_data.paginate(page=page, per_page=per_page, error_out=False)

        # Debug: ตรวจสอบค่าที่ถูกส่งไปยัง HTML
        print(f'Page: {page}')
        print(f'Per Page: {per_page}')
        print(f'Beds Data: {beds_data}')
        
        beds_by_dept = count_beds(selected_dept_name, selected_room_type)


        return render_template('deptAddmission.html', beds_data=beds_data, selected_per_page=per_page, beds_by_dept=beds_by_dept)
    

#หน้าdept Heart
@app.route("/deptHeart")

def deptHeart():

        # ดึงข้อมูลที่ผู้ใช้เลือกในฟอร์ม
        selected_room_type = request.args.get('room_id')
        selected_bed_type = request.args.get('bed_type')
        selected_dept_name = request.args.get('dept_name')
        selected_bed_status = request.args.get('bed_status')

        # อัปเดต query ในการดึงข้อมูล ใช้ join เพื่อเชื่อมข้อมูล 2 ตารางเข้ามาเพื่อใช้ในการค้นหาข้อมูลจากทั้ง2ตาราง
        beds_data = Beds.query.join(Rooms, Beds.room_id == Rooms.room_id)


        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        if selected_room_type and selected_room_type != 'Select Room Type':
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            print(f'Selected Bed Status: {selected_bed_status}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_status == selected_bed_status)


        # นับจำนวนข้อมูล ของ beds_data
        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        beds_data = beds_data.paginate(page=page, per_page=per_page, error_out=False)

        # Debug: ตรวจสอบค่าที่ถูกส่งไปยัง HTML
        print(f'Page: {page}')
        print(f'Per Page: {per_page}')
        print(f'Beds Data: {beds_data}')
        
        beds_by_dept = count_beds(selected_dept_name, selected_room_type)


        return render_template('deptHeart.html', beds_data=beds_data, selected_per_page=per_page, beds_by_dept=beds_by_dept)

#หน้าdept Surgery
@app.route("/deptSurgery")

def deptSurgery():

        # ดึงข้อมูลที่ผู้ใช้เลือกในฟอร์ม
        selected_room_type = request.args.get('room_id')
        selected_bed_type = request.args.get('bed_type')
        selected_dept_name = request.args.get('dept_name')
        selected_bed_status = request.args.get('bed_status')

        # อัปเดต query ในการดึงข้อมูล ใช้ join เพื่อเชื่อมข้อมูล 2 ตารางเข้ามาเพื่อใช้ในการค้นหาข้อมูลจากทั้ง2ตาราง
        beds_data = Beds.query.join(Rooms, Beds.room_id == Rooms.room_id)


        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        if selected_room_type and selected_room_type != 'Select Room Type':
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            print(f'Selected Bed Status: {selected_bed_status}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_status == selected_bed_status)


        # นับจำนวนข้อมูล ของ beds_data
        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        beds_data = beds_data.paginate(page=page, per_page=per_page, error_out=False)

        # Debug: ตรวจสอบค่าที่ถูกส่งไปยัง HTML
        print(f'Page: {page}')
        print(f'Per Page: {per_page}')
        print(f'Beds Data: {beds_data}')
        
        beds_by_dept = count_beds(selected_dept_name, selected_room_type)


        return render_template('deptSurgery.html', beds_data=beds_data, selected_per_page=per_page, beds_by_dept=beds_by_dept)

#หน้าdept Medicine
@app.route("/deptMedicine")

def deptMedicine():

        # ดึงข้อมูลที่ผู้ใช้เลือกในฟอร์ม
        selected_room_type = request.args.get('room_id')
        selected_bed_type = request.args.get('bed_type')
        selected_dept_name = request.args.get('dept_name')
        selected_bed_status = request.args.get('bed_status')

        # อัปเดต query ในการดึงข้อมูล ใช้ join เพื่อเชื่อมข้อมูล 2 ตารางเข้ามาเพื่อใช้ในการค้นหาข้อมูลจากทั้ง2ตาราง
        beds_data = Beds.query.join(Rooms, Beds.room_id == Rooms.room_id)


        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        if selected_room_type and selected_room_type != 'Select Room Type':
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            print(f'Selected Bed Status: {selected_bed_status}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_status == selected_bed_status)


        # นับจำนวนข้อมูล ของ beds_data
        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        beds_data = beds_data.paginate(page=page, per_page=per_page, error_out=False)

        # Debug: ตรวจสอบค่าที่ถูกส่งไปยัง HTML
        print(f'Page: {page}')
        print(f'Per Page: {per_page}')
        print(f'Beds Data: {beds_data}')
        
        beds_by_dept = count_beds(selected_dept_name, selected_room_type)


        return render_template('deptMedicine.html', beds_data=beds_data, selected_per_page=per_page, beds_by_dept=beds_by_dept)

#หน้าdept Pediatrics
@app.route("/deptPediatrics")

def deptPediatrics():

        # ดึงข้อมูลที่ผู้ใช้เลือกในฟอร์ม
        selected_room_type = request.args.get('room_id')
        selected_bed_type = request.args.get('bed_type')
        selected_dept_name = request.args.get('dept_name')
        selected_bed_status = request.args.get('bed_status')

        # อัปเดต query ในการดึงข้อมูล ใช้ join เพื่อเชื่อมข้อมูล 2 ตารางเข้ามาเพื่อใช้ในการค้นหาข้อมูลจากทั้ง2ตาราง
        beds_data = Beds.query.join(Rooms, Beds.room_id == Rooms.room_id)


        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        if selected_room_type and selected_room_type != 'Select Room Type':
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            print(f'Selected Bed Status: {selected_bed_status}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_status == selected_bed_status)


        # นับจำนวนข้อมูล ของ beds_data
        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        beds_data = beds_data.paginate(page=page, per_page=per_page, error_out=False)

        # Debug: ตรวจสอบค่าที่ถูกส่งไปยัง HTML
        print(f'Page: {page}')
        print(f'Per Page: {per_page}')
        print(f'Beds Data: {beds_data}')
        
        beds_by_dept = count_beds(selected_dept_name, selected_room_type)


        return render_template('deptPediatrics.html', beds_data=beds_data, selected_per_page=per_page, beds_by_dept=beds_by_dept)

#หน้าdept Obstetrics
@app.route("/deptObstetrics")

def deptObstetrics():

        # ดึงข้อมูลที่ผู้ใช้เลือกในฟอร์ม
        selected_room_type = request.args.get('room_id')
        selected_bed_type = request.args.get('bed_type')
        selected_dept_name = request.args.get('dept_name')
        selected_bed_status = request.args.get('bed_status')

        # อัปเดต query ในการดึงข้อมูล ใช้ join เพื่อเชื่อมข้อมูล 2 ตารางเข้ามาเพื่อใช้ในการค้นหาข้อมูลจากทั้ง2ตาราง
        beds_data = Beds.query.join(Rooms, Beds.room_id == Rooms.room_id)


        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        if selected_room_type and selected_room_type != 'Select Room Type':
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            print(f'Selected Bed Status: {selected_bed_status}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_status == selected_bed_status)


        # นับจำนวนข้อมูล ของ beds_data
        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        beds_data = beds_data.paginate(page=page, per_page=per_page, error_out=False)

        # Debug: ตรวจสอบค่าที่ถูกส่งไปยัง HTML
        print(f'Page: {page}')
        print(f'Per Page: {per_page}')
        print(f'Beds Data: {beds_data}')
        
        beds_by_dept = count_beds(selected_dept_name, selected_room_type)


        return render_template('deptObstetrics.html', beds_data=beds_data, selected_per_page=per_page, beds_by_dept=beds_by_dept)

#หน้าdept Other
@app.route("/deptOther")

def deptOther():

        # ดึงข้อมูลที่ผู้ใช้เลือกในฟอร์ม
        selected_room_type = request.args.get('room_id')
        selected_bed_type = request.args.get('bed_type')
        selected_dept_name = request.args.get('dept_name')
        selected_bed_status = request.args.get('bed_status')

        # อัปเดต query ในการดึงข้อมูล ใช้ join เพื่อเชื่อมข้อมูล 2 ตารางเข้ามาเพื่อใช้ในการค้นหาข้อมูลจากทั้ง2ตาราง
        beds_data = Beds.query.join(Rooms, Beds.room_id == Rooms.room_id)


        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        if selected_room_type and selected_room_type != 'Select Room Type':
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            print(f'Selected Bed Status: {selected_bed_status}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_status == selected_bed_status)


        # นับจำนวนข้อมูล ของ beds_data
        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        beds_data = beds_data.paginate(page=page, per_page=per_page, error_out=False)

        # Debug: ตรวจสอบค่าที่ถูกส่งไปยัง HTML
        print(f'Page: {page}')
        print(f'Per Page: {per_page}')
        print(f'Beds Data: {beds_data}')
        
        beds_by_dept = count_beds(selected_dept_name, selected_room_type)


        return render_template('deptOther.html', beds_data=beds_data, selected_per_page=per_page, beds_by_dept=beds_by_dept)

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



def count_beds(dept_name, room_type):
    # ดึงข้อมูลเตียงตามแผนกและห้อง
    beds_data = db.session.query(Beds.dept_name, Rooms.room_type, func.count().label('total_beds')) \
        .filter(Beds.room_id == Rooms.room_id) \
        .group_by(Beds.dept_name, Rooms.room_type)
    
    if dept_name and dept_name != 'Select Department':
        beds_data = beds_data.filter(Beds.dept_name == dept_name)
    
    if room_type and room_type != 'Select Room Type':
        beds_data = beds_data.filter(Rooms.room_type == room_type)
    
    beds_data = beds_data.all()

    # ดึงข้อมูลจำนวนเตียงที่ว่างและไม่ว่างตามแผนกและห้อง
    vacant_beds_data = db.session.query(Beds.dept_name, Rooms.room_type, func.count().label('vacant_beds')) \
        .filter(Beds.room_id == Rooms.room_id, Beds.bed_status == 'ว่าง') \
        .group_by(Beds.dept_name, Rooms.room_type)
    
    if dept_name and dept_name != 'Select Department':
        vacant_beds_data = vacant_beds_data.filter(Beds.dept_name == dept_name)
    
    if room_type and room_type != 'Select Room Type':
        vacant_beds_data = vacant_beds_data.filter(Rooms.room_type == room_type)
    
    vacant_beds_data = vacant_beds_data.all()

    # คำนวณจำนวนเตียงที่ไม่ว่างจากข้อมูลทั้งหมดและข้อมูลที่ว่าง
    occupied_beds_data = [(dept, room, total - vacant) for (dept, room, total) in beds_data for (dept_v, room_v, vacant) in vacant_beds_data if dept == dept_v and room == room_v]

    return {
        'total_beds': beds_data,
        'vacant_beds': vacant_beds_data,
        'occupied_beds': occupied_beds_data,
    }





@app.route("/slotbooking")
@login_required
def slotbooking():

        # ดึงข้อมูลที่ผู้ใช้เลือกในฟอร์ม
        selected_room_type = request.args.get('room_id')
        selected_bed_type = request.args.get('bed_type')
        selected_dept_name = request.args.get('dept_name')
        selected_bed_status = request.args.get('bed_status')

        # อัปเดต query ในการดึงข้อมูล ใช้ join เพื่อเชื่อมข้อมูล 2 ตารางเข้ามาเพื่อใช้ในการค้นหาข้อมูลจากทั้ง2ตาราง
        beds_data = Beds.query.join(Rooms, Beds.room_id == Rooms.room_id)


        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        if selected_room_type and selected_room_type != 'Select Room Type':
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            print(f'Selected Bed Status: {selected_bed_status}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_status == selected_bed_status)


        # นับจำนวนข้อมูล ของ beds_data
        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        beds_data = beds_data.paginate(page=page, per_page=per_page, error_out=False)

        # Debug: ตรวจสอบค่าที่ถูกส่งไปยัง HTML
        print(f'Page: {page}')
        print(f'Per Page: {per_page}')
        print(f'Beds Data: {beds_data}')
        
        beds_by_dept = count_beds(selected_dept_name, selected_room_type)


        return render_template('basebooking.html', beds_data=beds_data, selected_per_page=per_page, beds_by_dept=beds_by_dept)



# -------------------------------------#
#           TEST SLOT BED PAGE
# -------------------------------------#

@app.route('/index.php')
@login_required
def index_php():
    # check ว่าเป็น admin login อยู่ในระบบ อยู่ป่าว
    if('adminuser' in session and session['adminuser']==params['adminuser']):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 9999999, type=int)

        # ดึงข้อมูลที่ผู้ใช้เลือกในฟอร์ม
        selected_bed_type = request.args.get('bed_type')
        selected_dept_name = request.args.get('dept_name')
        selected_bed_status = request.args.get('bed_status')

        # อัปเดต query ในการดึงข้อมูล
        beds_data = Beds.query

        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter_by(bed_type=selected_bed_type)

        if selected_dept_name and selected_dept_name != 'Select Department':
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter_by(dept_name=selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            print(f'Selected Bed Status: {selected_bed_status}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter_by(bed_status=selected_bed_status)

        beds_data = beds_data.paginate(page=page, per_page=per_page, error_out=False)

        # Debug: ตรวจสอบค่าที่ถูกส่งไปยัง HTML
        print(f'Page: {page}')
        print(f'Per Page: {per_page}')
        print(f'Beds Data: {beds_data}')
        
        # for bed in beds_data:
        #     data.append({
        #         'bed_id': bed.bed_id,
        #         'room_id': bed.room_id,
        #         'bed_type' : bed.bed_type,
        #         'bed_status' : bed.bed_status,
        #         'dept_name' : bed.dept_name
        #         # เพิ่มข้อมูลอื่น ๆ ที่คุณต้องการดึงมาในนี้
        #     })

        # return render_template('index.php', data=data)
        return render_template('index.php', beds_data=beds_data, selected_per_page=per_page)
    else:
        flash("Login and try Again", "warning")
        return redirect('/admin')





# เพิ่มส่วนของการสร้างเส้นทางสำหรับการเพิ่มข้อมูลเตียง
@app.route('/insert_bed', methods=['GET', 'POST'])
# @login_required
def insert_bed():
     # check ว่าเป็น admin login อยู่ในระบบ อยู่ป่าว
    if('adminuser' in session and session['adminuser']==params['adminuser']):
        form = InsertForm()
        if form.validate_on_submit():
            bed_id = form.bed_id.data
            room_id = form.room_id.data
            bed_type = form.bed_type.data
            bed_status = form.bed_status.data
            dept_name = form.dept_name.data

            # เช็คเงื่อนไขเหมือนกับเส้นทาง '/addBedpage'
            bedID = Beds.query.filter_by(bed_id=bed_id).first()
            roomID = Rooms.query.filter_by(room_id=room_id).first()
            deptName = Departments.query.filter_by(dept_name=dept_name).first()

            if bedID:
                response = make_response('''
                <script>
                    alert('Bed ID is already Existed');
                    window.location.href = '/insert_bed';
                </script>
                ''')
                return response
                # flash("Bed ID is already Existed", "warning")
            elif not roomID:
                print("auan")
                response = make_response('''
                <script>
                    alert('Room ID doesn\\'t Exist');
                    window.location.href = '/insert_bed';
                </script>
                ''')
                return response
                # flash("Room ID doesn't Exist", "warning")
            elif not deptName:
                response = make_response('''
                <script>
                    alert("Department Name doesn't Exist");
                    window.location.href = '/insert_bed';
                </script>
                ''')
                return response
                # flash("Department doesn't Exist", "warning")
            else:
                new_bed = Beds(bed_id=bed_id, room_id=room_id, bed_type=bed_type, bed_status=bed_status, dept_name=dept_name)
                db.session.add(new_bed)
                db.session.commit()
                response = make_response('''
                <script>
                    alert('Record Inserted Successfully!');
                    window.location.href = '/index.php';
                </script>
                ''')
                return response
                # flash("Bed added successfully!", "success")
                # return redirect(url_for('index_php'))

        return render_template('insert_bed.html', form=form)

    else:
        flash("Login and try Again", "warning")
        return redirect('/admin')


# เพิ่มส่วนของการแก้ไขเตียง (Edit)
@app.route('/edit_bed/<bed_id>', methods=['GET', 'POST'])
# @login_required
def edit_bed(bed_id):
     # check ว่าเป็น admin login อยู่ในระบบ อยู่ป่าว
    if('adminuser' in session and session['adminuser']==params['adminuser']):
        # ดึงข้อมูลเตียงที่ต้องการแก้ไขจากฐานข้อมูล (ให้แก้ตามโมเดลของคุณ)
        bed = Beds.query.filter_by(bed_id=bed_id).first()

        if request.method == 'POST':
            # ดึงข้อมูลจากแบบฟอร์มแก้ไขและอัปเดตข้อมูลในฐานข้อมูล
            bed_id = request.form['bed_id']
            room_id = request.form['room_id']
            bed_type = request.form['bed_type']
            bed_status = request.form['bed_status']
            dept_name = request.form['dept_name']

            # เช็คเงื่อนไขเหมือนกับการเพิ่มเตียง
            bedID = Beds.query.filter_by(bed_id=bed_id).first()
            roomID = Rooms.query.filter_by(room_id=room_id).first()
            deptName = Departments.query.filter_by(dept_name=dept_name).first()

            if bedID and bedID != bed:
                response = make_response('''
                <script>
                    alert('Bed ID is already Existed');
                    window.location.href = '/edit_bed/{0}';
                </script>
                ''')
                return response

            elif not roomID:
                print("auan")
                response = make_response('''
                <script>
                    alert('Room ID doesn\\'t Exist');
                    window.location.href = '/insert_bed';
                </script>
                ''')
                return response

            elif not deptName:
                response = make_response('''
                <script>
                    alert("Department Name doesn't Exist");
                    window.location.href = '/insert_bed';
                </script>
                ''')
                return response

            bed.bed_id = bed_id
            bed.room_id = room_id
            bed.bed_type = bed_type
            bed.bed_status = bed_status
            bed.dept_name = dept_name
            db.session.commit()

            response = make_response('''
                <script>
                    alert('Updated Successfully!');
                    window.location.href = '/index.php';
                </script>
            ''')
            return response

        return render_template('edit_bed.html', bed=bed)

    else:
        flash("Login and try Again", "warning")
        return redirect('/admin')

# เพิ่มส่วนของการลบเตียง (Delete)
@app.route('/delete_bed/<bed_id>', methods=['GET'])
# @login_required
def delete_bed(bed_id):
     # check ว่าเป็น admin login อยู่ในระบบ อยู่ป่าว
    if('adminuser' in session and session['adminuser']==params['adminuser']):
        # ดึงข้อมูลเตียงที่ต้องการลบจากฐานข้อมูล (ให้แก้ตามโมเดลของคุณ)
        bed = Beds.query.filter_by(bed_id=bed_id).first()
        
        if bed:
            db.session.delete(bed)
            db.session.commit()
            response = make_response('''
                <script>
                    alert('Deleted Successfully!');
                    window.location.href = '/index.php';
                </script>
                ''')
            return response
            # flash('Bed deleted successfully!', 'success')
        else:

            response = make_response('''
                <script>
                    alert('Bed not found!!');
                    window.location.href = '/index.php';
                </script>
                ''')
            return response
            # flash('Bed not found!', 'danger')
        
        # return redirect(url_for('index_php'))  # หลังจากลบสำเร็จให้กลับไปที่หน้า index.php

    else:
        flash("Login and try Again", "warning")
        return redirect('/admin')


@app.route("/booking")
@login_required
def booking():

        # # ดึงข้อมูลที่ผู้ใช้เลือกในฟอร์ม
        # selected_room_type = request.args.get('room_id')
        # selected_bed_type = request.args.get('bed_type')
        # selected_dept_name = request.args.get('dept_name')
        # selected_bed_status = request.args.get('bed_status')

        # อัปเดต query ในการดึงข้อมูล ใช้ join เพื่อเชื่อมข้อมูล 2 ตารางเข้ามาเพื่อใช้ในการค้นหาข้อมูลจากทั้ง2ตาราง
        booking_data = Booking.query.join(Patients, Booking.pt_ssn == Patients.pt_ssn).join(Beds, Booking.bed_id == Beds.bed_id).add_columns(Booking.bk_id, Booking.pt_ssn, Booking.bed_id, \
            Booking.room_id, Booking.dept_id, Booking.user_id, Booking.bk_status, Booking.bk_ad_time,Patients.pt_fname, Patients.pt_lname, Beds.bed_type)

        print("*********************")
        print(booking_data)

        for i in booking_data:
            print(i.pt_fname)
            print(i.bed_id)

        booking_count = booking_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', booking_count, type=int)


        # if selected_room_type and selected_room_type != 'Select Room Type':
        #     print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
        #     booking_data = booking_data.filter(Rooms.room_type == selected_room_type)


        # if selected_bed_type and selected_bed_type != 'Select Bed Type':
        #     print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
        #     booking_data = booking_data.filter(Beds.bed_type == selected_bed_type)


        # if selected_dept_name and selected_dept_name != 'Select Department':
        #     print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
        #     booking_data = booking_data.filter(Beds.dept_name == selected_dept_name)

        # if selected_bed_status and selected_bed_status != 'Select Bed Status':
        #     print(f'Selected Bed Status: {selected_bed_status}')  # Debug: ตรวจสอบค่าที่รับมา
        #     booking_data = booking_data.filter(Beds.bed_status == selected_bed_status)


        # นับจำนวนข้อมูล ของ booking_data
        booking_count = booking_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', booking_count, type=int)


        booking_data = booking_data.paginate(page=page, per_page=per_page, error_out=False)

        # Debug: ตรวจสอบค่าที่ถูกส่งไปยัง HTML
        print(f'Page: {page}')
        print(f'Per Page: {per_page}')
        print(f'Booking Data: {booking_data}')

        return render_template('booking_kao.html', booking_data=booking_data, selected_per_page=per_page)


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