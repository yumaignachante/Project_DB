
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



from flask import Flask, json,redirect,render_template,flash,request, jsonify
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

class Patients(db.Model):
    pt_ssn=db.Column(db.String(13),primary_key=True)
    pt_fname=db.Column(db.String(50))
    pt_lname=db.Column(db.String(50))
    pt_dob=db.Column(db.Date)
    pt_age=db.Column(db.Integer)
    pt_gender=db.Column(db.String(25))
    pt_adn=db.Column(db.String(11))
    pt_phone_number=db.Column(db.String(12))
    trauma_id=db.Column(db.String(25))

    def get_id(self):
        return str(self.pt_ssn)
    
class Booking(db.Model):
    bk_id=db.Column(db.Integer,primary_key=True)
    pt_ssn = db.Column(db.String(13), db.ForeignKey('patients.pt_ssn'))  # เชื่อมกับตาราง patients
    bed_id = db.Column(db.String(25), db.ForeignKey('beds.bed_id'))  # เชื่อมกับตาราง beds
    room_id =db.Column(db.String(25))
    dept_id =db.Column(db.Integer)
    user_id =db.Column(db.Integer)
    bk_ad_time = db.Column(db.DateTime, default=datetime.utcnow)  # เวลาที่สร้างรายการ
    bk_update_time = db.Column(db.DateTime, onupdate=datetime.utcnow)  # เวลาที่อัปเดตรายการ
    bk_status =db.Column(db.String(25))


    def get_id(self):
        return str(self.bk_id)

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
            flash(f'Selected Room Type: {selected_room_type}')
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            flash(f'Selected Bed Type: {selected_bed_type}')
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            flash(f'Selected Department: {selected_dept_name}')
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            flash(f'Selected Bed Status: {selected_bed_status}')
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
            flash(f'Selected Room Type: {selected_room_type}')
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            flash(f'Selected Bed Type: {selected_bed_type}')
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            flash(f'Selected Department: {selected_dept_name}')
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            flash(f'Selected Bed Status: {selected_bed_status}')
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
            flash(f'Selected Room Type: {selected_room_type}')
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            flash(f'Selected Bed Type: {selected_bed_type}')
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            flash(f'Selected Department: {selected_dept_name}')
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            flash(f'Selected Bed Status: {selected_bed_status}')
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
            flash(f'Selected Room Type: {selected_room_type}')
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            flash(f'Selected Bed Type: {selected_bed_type}')
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            flash(f'Selected Department: {selected_dept_name}')
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            flash(f'Selected Bed Status: {selected_bed_status}')
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
            flash(f'Selected Room Type: {selected_room_type}')
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            flash(f'Selected Bed Type: {selected_bed_type}')
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            flash(f'Selected Department: {selected_dept_name}')
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            flash(f'Selected Bed Status: {selected_bed_status}')
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
            flash(f'Selected Room Type: {selected_room_type}')
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            flash(f'Selected Bed Type: {selected_bed_type}')
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            flash(f'Selected Department: {selected_dept_name}')
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            flash(f'Selected Bed Status: {selected_bed_status}')
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
            flash(f'Selected Room Type: {selected_room_type}')
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            flash(f'Selected Bed Type: {selected_bed_type}')
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            flash(f'Selected Department: {selected_dept_name}')
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            flash(f'Selected Bed Status: {selected_bed_status}')
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

        beds_bk_data = beds_data.join(Booking, Beds.bed_id == Booking.bed_id)


        for i in beds_bk_data:
            # print(i.bed_id)
            for j in beds_data:
                if j.bed_id == i.bed_id:
                    j = Beds.query.filter_by(bed_id=i.bed_id).first()
                    j.bed_status = "ไม่ว่าง"
                    db.session.commit()


        # update ข้อมูล สถานะเตียงที่ไม่ว่าง (มีข้อมูลเตียงในตาราง Booking)
        beds_data = Beds.query.join(Rooms, Beds.room_id == Rooms.room_id)

            



        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        if selected_room_type and selected_room_type != 'Select Room Type':
            flash(f'Selected Room Type: {selected_room_type}')
            print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            flash(f'Selected Bed Type: {selected_bed_type}')
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


        if selected_dept_name and selected_dept_name != 'Select Department':
            flash(f'Selected Department: {selected_dept_name}')
            print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
            beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

        if selected_bed_status and selected_bed_status != 'Select Bed Status':
            flash(f'Selected Bed Status: {selected_bed_status}')
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


        return render_template('basebooking.html', beds_data=beds_data, selected_per_page=per_page, beds_by_dept=beds_by_dept, selected_room_type=selected_room_type, selected_bed_status=selected_bed_status)



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


        # นับจำนวนข้อมูล ของ beds_data
        beds_count = beds_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', beds_count, type=int)


        beds_data = beds_data.paginate(page=page, per_page=per_page, error_out=False)

        # Debug: ตรวจสอบค่าที่ถูกส่งไปยัง HTML
        print(f'Page: {page}')
        print(f'Per Page: {per_page}')
        print(f'Beds Data: {beds_data}')
        

        return render_template('index.php', beds_data=beds_data, selected_per_page=per_page)


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
        # return render_template('index.php', beds_data=beds_data, selected_per_page=per_page)
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

    bed_bk_pt_info = Beds.query.join(Booking, Beds.bed_id == Booking.bed_id).join(Patients, Booking.pt_ssn == Patients.pt_ssn) \
        .filter(Beds.bed_id == bed_id) \
        .first()

     # check ว่าเป็น admin login อยู่ในระบบ อยู่ป่าว
    # if('adminuser' in session and session['adminuser']==params['adminuser']):
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
        

    if bed_bk_pt_info:
            booking_info = Booking.query.filter_by(bed_id=bed.bed_id).first()
            if booking_info:
                bed.bed_status = 'ไม่ว่าง'
                db.session.commit()


                bed.pt_ssn = booking_info.pt_ssn

                
                # ระบุข้อมูลคนไข้เฉพาะเมื่อมีข้อมูลการจอง (booking_info ไม่เป็น None)
                patient_info = Patients.query.filter_by(pt_ssn=booking_info.pt_ssn).first()
                if patient_info:
                    bed.pt_fname = patient_info.pt_fname
                    bed.pt_lname = patient_info.pt_lname
                    bed.pt_dob = patient_info.pt_dob
                    bed.pt_age = patient_info.pt_age
                    bed.pt_gender = patient_info.pt_gender
                    bed.pt_adn = patient_info.pt_adn
                    bed.pt_phone_number = patient_info.pt_phone_number
                    bed.trauma_id = patient_info.trauma_id
            else:
                # ไม่มีการจองสำหรับเตียงนี้
                bed.pt_ssn = None
                bed.pt_fname = None
                bed.pt_lname = None
                bed.pt_dob = None
                bed.pt_age = None
                bed.pt_gender = None
                bed.pt_adn = None
                bed.pt_phone_number = None
                bed.trauma_id = None

    return render_template('edit_bed.html', bed=bed)


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






# เส้นทางสำหรับดึงข้อมูลผู้ป่วย
@app.route('/get_patient_data', methods=['GET'])
def get_patient_data():
    pt_ssn = request.args.get('pt_ssn')
    bed_id = request.args.get('bed_id')

    if pt_ssn:
        # ดำเนินการดึงข้อมูลผู้ป่วยจากฐานข้อมูลของคุณ หรือแหล่งข้อมูลอื่น ๆ
        pt_data = Patients.query.filter_by(pt_ssn=pt_ssn).first()

        if pt_data is not None:
            print("# แปลงข้อมูลผู้ป่วยเป็นพจน์ Python")
            # แปลงข้อมูลผู้ป่วยเป็นพจน์ Python
            patient_info = {
                "pt_ssn": pt_data.pt_ssn,
                "pt_fname": pt_data.pt_fname,
                "pt_lname": pt_data.pt_lname,
                "pt_dob": pt_data.pt_dob.strftime("%Y-%m-%d"),  # แปลงเป็นรูปแบบวันที่
                "pt_age": pt_data.pt_age,
                "pt_gender": pt_data.pt_gender,
                "pt_adn": pt_data.pt_adn,
                "pt_phone_number": pt_data.pt_phone_number,
                "trauma_id": pt_data.trauma_id
            }

            print(pt_data.pt_ssn,pt_data.pt_fname,pt_data.pt_lname,pt_data.pt_dob.strftime("%Y-%m-%d"),pt_data.pt_age,pt_data.pt_gender,pt_data.pt_adn,pt_data.pt_phone_number,pt_data.trauma_id)
        else:
            print("กรณีไม่พบข้อมูลผู้ป่วย")
            # กรณีไม่พบข้อมูลผู้ป่วย
            patient_info = {
                "error": "Patient not found"
            }
    else:
        print("หากไม่ได้รับ pt_ssn จากคำขอ")
        # หากไม่ได้รับ pt_ssn จากคำขอ
        patient_info = {}

    # ส่ง JSON กลับไปยังไคลเอนต์
    return jsonify(patient_info)




# เพิ่มส่วนของการจองเตียง (Booking)
@app.route('/booking_/<bed_id>', methods=['GET', 'POST'])
# @login_required
def booking_bed(bed_id):
    #  # check ว่าเป็น admin login อยู่ในระบบ อยู่ป่าว
    # if('adminuser' in session and session['adminuser']==params['adminuser']):


        # ดึงข้อมูลเตียงที่ต้องการแก้ไขจากฐานข้อมูล (ให้แก้ตามโมเดลของคุณ)
        bed = Beds.query.filter_by(bed_id=bed_id).first()

        beds_rooms = Beds.query.join(Rooms, Beds.room_id == Rooms.room_id).add_columns(Beds.bed_id, Rooms.room_type)
        for i in beds_rooms:
            if bed_id == i.bed_id:
                print(i.room_type)
                bed.room_type = i.room_type

        if request.method == 'POST':
            # ดึงข้อมูลจากแบบฟอร์มแก้ไขและอัปเดตข้อมูลในฐานข้อมูล
            pt_ssn = request.form['pt_ssn']
            bed_id = request.form['bed_id']
            room_id = request.form['room_id']
            dept_name = request.form['dept_name']
            bed_status = request.form['bed_status']

            # เช็คเงื่อนไขเหมือนกับการเพิ่มเตียง
            bedID = Beds.query.filter_by(bed_id=bed_id).first()
            roomID = Rooms.query.filter_by(room_id=room_id).first()
            deptName = Departments.query.filter_by(dept_name=dept_name).first()

            # check ว่า bed_id มีอยู่แล้วมั้ยในตาราง Beds
            if bedID and bedID != bed:
                response = make_response('''
                <script>
                    alert('Bed ID is already Exist');
                    window.location.href = '/slotbooking';
                </script>
                ''')
                return response

            elif not roomID:
                print("auan")
                response = make_response('''
                <script>
                    alert('Room ID doesn\\'t Exist');
                    window.location.href = '/slotbooking';
                </script>
                ''')
                return response

            elif not deptName:
                response = make_response('''
                <script>
                    alert("Department Name doesn't Exist");
                    window.location.href = '/slotbooking';
                </script>
                ''')
                return response

            bed.bed_id = bed_id
            bed.room_id = room_id
            bed.bed_type = bedID.bed_type
            bed.bed_status = bed_status
            bed.dept_name = dept_name


            # db.session.commit()

        pt_ssn = request.args.get('pt_ssn')
        bed_id = request.args.get('bed_id')

        if pt_ssn == '':
            patient_info = {
                                "pt_ssn": '',
                                "pt_fname": '',
                                "pt_lname": '',
                                "pt_dob": '',
                                "pt_age": '',
                                "pt_gender": '',
                                "pt_adn": '',
                                "pt_phone_number": '',
                                "trauma_id": ''
                            }
            return jsonify(patient_info)

        # รหัสที่เหลือของฟังก์ชัน booking_bed ในส่วนนี้...
        if pt_ssn and bed_id:
            print("ssnเข้า")
            pt_data = Patients.query.filter_by(pt_ssn=pt_ssn).first()
            
            if pt_data:
                print("พบข้อมูลผู้ป่วย")
                patient_info = {
                    "pt_ssn": pt_data.pt_ssn,
                    "pt_fname": pt_data.pt_fname,
                    "pt_lname": pt_data.pt_lname,
                    "pt_dob": pt_data.pt_dob.strftime("%Y-%m-%d"),  # แปลงเป็นรูปแบบวันที่
                    "pt_age": pt_data.pt_age,
                    "pt_gender": pt_data.pt_gender,
                    "pt_adn": pt_data.pt_adn,
                    "pt_phone_number": pt_data.pt_phone_number,
                    "trauma_id": pt_data.trauma_id
                }
                return jsonify(patient_info)
            else:
                print("ไม่พบ")
                # หากไม่พบข้อมูลผู้ป่วย
                patient_info = {}
                return jsonify(patient_info)
                
        else:
            print("ไม่ได้รับ")
            # หากไม่ได้รับ pt_ssn จากคำขอ
            patient_info = {}

        if request.method == 'POST':
            pt_ssn = request.form['pt_ssn']
            bed_id = request.form['bed_id']
            room_id = request.form['room_id']
            dept_name = request.form['dept_name']
            # bed_status = request.form['bed_status']

            # ตรวจสอบข้อมูลผู้ป่วย และเตียงว่าถูกต้องหรือไม่ (เช่น ต้องมีในฐานข้อมูล)
            pt_data = Patients.query.filter_by(pt_ssn=pt_ssn).first()
            bed_data = Beds.query.filter_by(bed_id=bed_id).first()
            room_data = Rooms.query.filter_by(room_id=room_id).first()

            room_dept = Rooms.query.join(Departments, Rooms.dept_name == Departments.dept_name).add_columns(Rooms.room_id, Departments.dept_id)

            for j in room_dept:
                if room_id == j.room_id:
                    dept_id = j.dept_id


            if pt_data and bed_data and room_data:
                # สร้างรายการการจองใหม่
                booking = Booking(
                    pt_ssn=pt_ssn,
                    bed_id=bed_id,
                    room_id=room_id,
                    dept_id=dept_id,  # หรือใช้ id ของแผนกแทน
                    user_id=current_user.user_id,  # ใช้ข้อมูลผู้ใช้ที่เข้าสู่ระบบ
                    bk_status='รอดำเนินการ..'
                )

                # เพิ่มรายการการจองลงในฐานข้อมูล
                db.session.add(booking)
                db.session.commit()

                # หลังจากบันทึกการจองสำเร็จ คุณสามารถดำเนินการเพิ่มส่วนอื่น ๆ ตามที่คุณต้องการ เช่น แสดงข้อความสำเร็จหรือเปลี่ยนหน้าไปยังหน้าอื่น

                # เช่น แสดงข้อความสำเร็จและเปลี่ยนหน้าไปยังหน้าอื่น
                response = make_response('''
                    <script>
                        alert("Booking Successfully!");
                        window.location.href = '/slotbooking';
                    </script>
                    ''')
                return response

            else:
                response = make_response('''
                    <script>
                        alert("Error !!!");
                        window.location.href = '/slotbooking';
                    </script>
                    ''')
                return response
        

            

        # หลังจากที่รับข้อมูลผู้ป่วยเรียบร้อยแล้ว ก่อนส่งข้อมูลไปยังเทมเพลต
        # ให้รีเฟรชหน้าเพื่อให้ข้อมูลผู้ป่วยถูกแสดงในช่องอื่น ๆ ในหน้า booking_bed
        return render_template('booking_bed.html', bed=bed, patient_info={})












@app.route("/booking")
@login_required
def booking():

        # # ดึงข้อมูลที่ผู้ใช้เลือกในฟอร์ม

        selected_bed_type = request.args.get('bed_type')
        selected_booking_status = request.args.get('bk_status')

        # อัปเดต query ในการดึงข้อมูล ใช้ join เพื่อเชื่อมข้อมูล 2 ตารางเข้ามาเพื่อใช้ในการค้นหาข้อมูลจากทั้ง2ตาราง
        booking_data = Booking.query.join(Patients, Booking.pt_ssn == Patients.pt_ssn).join(Beds, Booking.bed_id == Beds.bed_id).add_columns(Booking.bk_id, Booking.pt_ssn, Booking.bed_id, \
            Booking.room_id, Booking.dept_id, Booking.user_id, Booking.bk_status, Booking.bk_ad_time,Patients.pt_fname, Patients.pt_lname, Beds.bed_type, Booking.bk_update_time)

        print("*********************")
        print(booking_data)

        for i in booking_data:
            print(i.pt_fname)
            print(i.bed_id)
            print(i.bk_update_time)

        booking_count = booking_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', booking_count, type=int)


        # if selected_room_type and selected_room_type != 'Select Room Type':
        #     print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
        #     booking_data = booking_data.filter(Rooms.room_type == selected_room_type)


        if selected_bed_type and selected_bed_type != 'Select Bed Type':
            print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
            booking_data = booking_data.filter(Beds.bed_type == selected_bed_type)


        # if selected_dept_name and selected_dept_name != 'Select Department':
        #     print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
        #     booking_data = booking_data.filter(Beds.dept_name == selected_dept_name)

        if selected_booking_status and selected_booking_status != 'Select Booking Status':
            print(f'Selected Booking Status: {selected_booking_status}')  # Debug: ตรวจสอบค่าที่รับมา
            booking_data = booking_data.filter(Booking.bk_status == selected_booking_status)


        # นับจำนวนข้อมูล ของ booking_data
        booking_count = booking_data.count()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', booking_count, type=int)


        booking_data = booking_data.paginate(page=page, per_page=per_page, error_out=False)

        # Debug: ตรวจสอบค่าที่ถูกส่งไปยัง HTML
        print(f'Page: {page}')
        print(f'Per Page: {per_page}')
        print(f'Booking Data: {booking_data}')

        return render_template('booking_kao.html', booking_data=booking_data, selected_per_page=per_page, selected_bed_type=selected_bed_type, selected_booking_status=selected_booking_status)




# เพิ่มส่วนของการลบการจอง (Delete)
@app.route('/delete_booking/<booking_id>', methods=['GET', 'POST'])
# @login_required
def delete_booking(booking_id):
     # check ว่าเป็น admin login อยู่ในระบบ อยู่ป่าว
    if('adminuser' in session and session['adminuser']==params['adminuser']):
        # ดึงข้อมูลการจองที่ต้องการลบจากฐานข้อมูล (ให้แก้ตามโมเดลของคุณ)
        booking = Booking.query.filter_by(bk_id=booking_id).first()

        if booking:
            print("มี bk อยู่")
            
            # หาเตียงที่เกี่ยวข้องกับการจองนี้
            bed = Beds.query.get(booking.bed_id)

            if bed:
                # อัปเดต bed_status เป็น "ว่าง"
                bed.bed_status = "ว่าง"
                db.session.commit()

            # ลบการจอง
            db.session.delete(booking)
            db.session.commit()
            
            response = make_response('''
                <script>
                    alert('Deleted Successfully!');
                    window.location.href = '/booking';
                </script>
            ''')
            return response
        else:
            print("ไม่เจอ")
            response = make_response('''
                <script>
                    alert('Booking not found!!');
                    window.location.href = '/booking';
                </script>
            ''')
            return response
    else:
        flash("Login and try Again", "warning")
        return redirect('/admin')



# #หน้า bed booking
# @app.route("/bedbooking")

# def bedbooking():



#         # ดึงข้อมูลที่ผู้ใช้เลือกในฟอร์ม
#         selected_room_type = request.args.get('room_id')
#         selected_bed_type = request.args.get('bed_type')
#         selected_dept_name = request.args.get('dept_name')
#         selected_bed_status = request.args.get('bed_status')

#         # อัปเดต query ในการดึงข้อมูล ใช้ join เพื่อเชื่อมข้อมูล 2 ตารางเข้ามาเพื่อใช้ในการค้นหาข้อมูลจากทั้ง2ตาราง
#         beds_data = Beds.query.join(Rooms, Beds.room_id == Rooms.room_id)


#         beds_count = beds_data.count()

#         page = request.args.get('page', 1, type=int)
#         per_page = request.args.get('per_page', beds_count, type=int)


#         if selected_room_type and selected_room_type != 'Select Room Type':
#             flash(f'Selected Room Type: {selected_room_type}')
#             print(f'Selected Room Type: {selected_room_type}')  # Debug: ตรวจสอบค่าที่รับมา
#             beds_data = beds_data.filter(Rooms.room_type == selected_room_type)


#         if selected_bed_type and selected_bed_type != 'Select Bed Type':
#             flash(f'Selected Bed Type: {selected_bed_type}')
#             print(f'Selected Bed Type: {selected_bed_type}')  # Debug: ตรวจสอบค่าที่รับมา
#             beds_data = beds_data.filter(Beds.bed_type == selected_bed_type)


#         if selected_dept_name and selected_dept_name != 'Select Department':
#             flash(f'Selected Department: {selected_dept_name}')
#             print(f'Selected Department: {selected_dept_name}')  # Debug: ตรวจสอบค่าที่รับมา
#             beds_data = beds_data.filter(Beds.dept_name == selected_dept_name)

#         if selected_bed_status and selected_bed_status != 'Select Bed Status':
#             flash(f'Selected Bed Status: {selected_bed_status}')
#             print(f'Selected Bed Status: {selected_bed_status}')  # Debug: ตรวจสอบค่าที่รับมา
#             beds_data = beds_data.filter(Beds.bed_status == selected_bed_status)


#         # นับจำนวนข้อมูล ของ beds_data
#         beds_count = beds_data.count()

#         page = request.args.get('page', 1, type=int)
#         per_page = request.args.get('per_page', beds_count, type=int)


#         beds_data = beds_data.paginate(page=page, per_page=per_page, error_out=False)

#         # Debug: ตรวจสอบค่าที่ถูกส่งไปยัง HTML
#         print(f'Page: {page}')
#         print(f'Per Page: {per_page}')
#         print(f'Beds Data: {beds_data}')
        
#         beds_by_dept = count_beds(selected_dept_name, selected_room_type)
        
#         return render_template("bedbooking.php", beds_data=beds_data, selected_per_page=per_page, beds_by_dept=beds_by_dept, selected_room_type=selected_room_type, selected_bed_status=selected_bed_status)


# เพิ่มส่วนของการแก้ไขการจอง (Edit)
@app.route('/edit_booking/<booking_id>', methods=['GET', 'POST'])
@login_required
def edit_booking(booking_id):
    # ดึงข้อมูลการจองที่ต้องการแก้ไขจากฐานข้อมูล
    booking_join = Booking.query.join(Patients, Booking.pt_ssn == Patients.pt_ssn).join(Beds, Booking.bed_id == Beds.bed_id).add_columns(Booking.bk_id, Booking.pt_ssn, Booking.bed_id, \
        Booking.room_id, Booking.dept_id, Booking.user_id, Booking.bk_status, Booking.bk_ad_time,Patients.pt_fname, Patients.pt_lname, Beds.bed_type, Booking.bk_update_time)
    
    booking = Booking.query.filter_by(bk_id=booking_id).first()

    for i in booking_join:
        if str(i.bk_id) == str(booking_id):
            print(i.pt_fname)
            booking.pt_fname = i.pt_fname
            booking.pt_lname = i.pt_lname
            booking.bed_type = i.bed_type
                # booking.bed_status = i.bed_status
    # ตรวจสอบว่าผู้ใช้เป็น admin หรือไม่
    if current_user.username == 'admin':
        if request.method == 'POST':
            # ดึงข้อมูลจากแบบฟอร์มแก้ไข
            bk_ad_time = request.form['bk_ad_time']
            bk_update_time = datetime.now()  # เวลาปัจจุบัน
            bk_id = request.form['bk_id']
            bed_id = request.form['bed_id']
            pt_ssn = request.form['pt_ssn']
            pt_fname = request.form['pt_fname']
            pt_lname = request.form['pt_lname']
            room_id = request.form['room_id']
            bed_type = request.form['bed_type']
            user_id = request.form['user_id']
            bk_status = request.form['bk_status']
            # เวลาการจองไม่ควรสามารถแก้ไขได้
            # booking.bk_ad_time = request.form['bk_ad_time']
            # เวลาอัปเดตจะถูกอัปเดตโดยอัตโนมัติ
            # booking.bk_update_time = request.form['bk_update_time']

            # อัปเดตข้อมูลการจอง
            booking.bk_ad_time = bk_ad_time
            booking.bk_update_time = bk_update_time
            booking.bk_id = bk_id
            booking.bed_id = bed_id
            booking.pt_ssn = pt_ssn
            booking.pt_fname = pt_fname
            booking.pt_lname = pt_lname
            booking.room_id = room_id
            booking.bed_type = bed_type
            booking.user_id = user_id
            booking.bk_status = bk_status

            # บันทึกการเปลี่ยนแปลงลงในฐานข้อมูล
            db.session.commit()

            # ลิ้งค์กลับไปยังหน้ารายการจอง
            response = make_response('''
                <script>
                    alert('Updated Successfully!');
                    window.location.href = '/booking';
                </script>
            ''')
            return response
        
        # แสดงหน้าแก้ไขการจอง
        return render_template('edit_booking.html', booking=booking)
    
    else:
        flash("Login as admin to access this page", "warning")
        return redirect('/booking')








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