from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify, json, current_app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from db import get_patient_collection, get_doctor_collection
from forms import SignUp_patient, LoginForm, EditProfile_patient, ChangePassword, SignUp_doctor, EditProfile_doctor
from bson.objectid import ObjectId
import os



auth = Blueprint("auth", __name__)

load_dotenv()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





@auth.route("/appointments", methods=['GET', 'POST'])
def appointments():
    user_id = session.get("user_id")
    user_type = session.get("user_type")

    if not user_id or not user_type:
        flash("Please log in first.", "alert-danger")
        return redirect(url_for("auth.login"))

    if user_type == "patient":
        # 환자의 예약 정보 불러오기
        user_data = get_patient_collection().find_one({"_id": ObjectId(user_id)})
        appointments = user_data.get("appointments", [])
        
        # 의사 정보를 예약과 함께 병합하기
        enriched_appointments = []
        for a in appointments:
            doctor = get_doctor_collection().find_one({"_id": ObjectId(a["doctor_id"])})
            if doctor:
                a["doctor_image"] = doctor.get("image")
                a["doctor_name"] = f"{doctor['first_name']} {doctor['last_name']}"
                a["doctor_specialization"] = doctor.get("specialization")
                a["doctor_hospital_name"] = doctor.get("hospital_name")
                a["doctor_address"] = doctor.get("address")
                a["doctor_preferred_language"] = doctor.get("preferred_language")
                a["doctor_bio"] = doctor.get("bio")
                a["doctor_phone"] = doctor.get("phone")
                a["doctor_rating"] = doctor.get("rating")
            enriched_appointments.append(a)

        return render_template("appointments.html", appointments=enriched_appointments, user_type="patient")

    elif user_type == "doctor":
        # 의사의 환자 예약 정보 불러오기
        doctor_data = get_doctor_collection().find_one({"_id": ObjectId(user_id)})
        appointments = doctor_data.get("appointments", [])

        # 환자 정보를 예약과 함께 병합하기
        enriched_appointments = []
        for a in appointments:
            patient = get_patient_collection().find_one({"_id": ObjectId(a["patient_id"])})
            if patient:
                a["patient_name"] = f"{patient['first_name']} {patient['last_name']}"
                a["patient_phone"] = patient.get("phone")
                a["patient_birth"] = patient.get("birth")
                a["patient_sex"] = patient.get("sex")
                a["patient_insurance"] = patient.get("insurance")
                a["patient_preferred_language"] = patient.get("preferred_language")
                a["patient_medical_history"] = patient.get("medical_history")
                a["patient_comments_for_doctor"] = patient.get("comments_for_doctor")
            enriched_appointments.append(a)

        return render_template("appointments.html", appointments=enriched_appointments, user_type="doctor")

    else:
        flash("Invalid user type.", "alert-danger")
        return redirect(url_for("views.landing_page"))






@auth.route('/login_security', methods=['GET', 'POST'])
def login_security():
    form = ChangePassword()

    user_type = session.get('user_type')
    user_email = session.get('user')

    if not user_email:
        flash('Please log in first.', 'alert-danger')
        return redirect(url_for('auth.login'))

    user = get_patient_collection().find_one({"email": user_email}) if user_type == 'patient' else get_doctor_collection().find_one({"email": user_email})
    
    if request.method == 'POST' and form.validate_on_submit():
        if not user:
            flash('User not found.', 'alert-danger')
            return redirect(url_for('auth.login'))

        if not check_password_hash(user['password'], form.current_password.data):
            flash('Current password is incorrect.', 'alert-danger')
            return render_template('login_security.html', form=form, user=user)
        
        if user['password'] == form.current_password.data:
            flash('New password must be different from the current password.', 'alert-danger')
            return render_template('login_security.html', form=form, user=user)

        if form.new_password.data != form.confirm_password.data:
            flash('New password and confirmation do not match.', 'alert-danger')
            return render_template('login_security.html', form=form, user=user)

        new_password_hash = generate_password_hash(form.new_password.data, method="pbkdf2:sha256")

        collection = get_patient_collection() if user_type == 'patient' else get_doctor_collection()
        collection.update_one(
            {"email": user_email},
            {
                "$set": {
                    "password": new_password_hash,
                    "updated_at": datetime.now()
                }
            }
        )

        flash('Password has been updated.', 'alert-success')

        return redirect(url_for('auth.login_security'))

    return render_template('login_security.html', form=form, user=user)





@auth.route("/myaccount", methods=["GET", "POST"])
def myAccount():
    user_type = session.get('user_type')
    user_email = session.get('user')

    user = None
    form = None
    filename = None

    if user_type == 'patient':
        user = get_patient_collection().find_one({"email": user_email})
        form = EditProfile_patient()
    elif user_type == 'doctor':
        user = get_doctor_collection().find_one({"email": user_email})
        form = EditProfile_doctor()

    if not user:
        flash("Your account was not found. Please log in again.", "alert-danger")
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        from_user_data(form, user)

    if request.method == 'POST' and 'image' in request.files:
        if 'image' not in request.files:
            flash('No file part', 'alert-danger')
            return redirect(request.url)
        
        file = request.files['image']
        if file.filename == '':
            flash('No selected file', 'alert-danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

    if form.validate_on_submit():
        update_data = {
            "first_name": form.first_name.data.capitalize(),
            "last_name": form.last_name.data.capitalize(),
            "phone": form.phone.data,
            "birth": form.birth.data.strftime('%Y-%m-%d'),
            "sex": form.sex.data,
            "preferred_language": form.preferred_language.data,
            "updated_at": datetime.now(),
        }

        if user_type == 'patient':
            update_data.update({
                "insurance": form.insurance.data,
                "address": form.address.data,
                "medical_history": form.medical_history.data.capitalize(),
                "comments_for_doctor": form.comments_for_doctor.data.capitalize(),
            })
        elif user_type == 'doctor':
            if filename:
                update_data['image'] = filename
            update_data.update({
                "medical_school": form.medical_school.data,
                "specialization": form.specialization.data,
                "graduation_year": form.graduation_year.data,
                "license_number": form.license_number.data,
                "address": form.address.data,
                "hospital_name": form.hospital_name.data,
                "bio": form.bio.data.capitalize(),
                "operating_hours": json.loads(form.operating_hours.data) if form.operating_hours.data else None,
            })

        update_user_profile(get_patient_collection() if user_type == 'patient' else get_doctor_collection(), user_email, update_data)
        flash("Profile updated successfully!", "alert-success")
        return redirect(url_for('auth.myAccount'))

    return render_template('myAccount.html', form=form, user=user, editing=request.args.get('edit'))

def update_user_profile(collection, email, update_data):
    collection.update_one({"email": email}, {"$set": update_data})

def from_user_data(form, user):
    form.first_name.data = user.get('first_name')
    form.last_name.data = user.get('last_name')
    form.phone.data = user.get('phone')
    form.birth.data = datetime.strptime(user['birth'], '%Y-%m-%d')
    form.sex.data = user.get('sex')
    form.preferred_language.data = user.get('preferred_language')

    if 'insurance' in user:
        form.insurance.data = user.get('insurance')
        form.address.data = user.get('address')
        form.medical_history.data = user.get('medical_history')
        form.comments_for_doctor.data = user.get('comments_for_doctor')
    else:
        form.image.data = user.get('image', 'default.png')
        form.specialization.data = user.get('specialization')
        form.license_number.data = user.get('license_number')
        form.medical_school.data = user.get('medical_school')
        form.graduation_year.data = user.get('graduation_year')
        form.address.data = user.get('address')
        form.hospital_name.data = user.get('hospital_name')
        form.bio.data = user.get('bio')
        operating_hours = user.get('operating_hours')
        form.operating_hours.data = json.dumps(operating_hours) if operating_hours else ''



@auth.route("/signup_doctor", methods=["GET", "POST"])
def signUp_doctor():
    form = SignUp_doctor()
    
    if form.validate_on_submit():
        if 'image' not in request.files:
            flash('No file part', 'alert-danger')
            return redirect(request.url)
        
        file = request.files['image']
        if file.filename == '':
            flash('No selected file', 'alert-danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

            try:
                password_hash = generate_password_hash(form.password.data, method="pbkdf2:sha256")
                user = {
                    "user_type": "doctor".capitalize(),
                    "image": filename,
                    "first_name": form.first_name.data.capitalize(),
                    "last_name": form.last_name.data.capitalize(),
                    "phone": form.phone.data,
                    "birth": form.birth.data.strftime('%Y-%m-%d'),
                    "sex": form.sex.data,
                    "preferred_language": form.preferred_language.data,
                    "medical_school": form.medical_school.data,
                    "specialization": form.specialization.data,
                    "graduation_year": form.graduation_year.data,
                    "license_number": form.license_number.data,
                    "email": form.email.data,
                    "password": password_hash,
                    "address": form.address.data,
                    "hospital_name": form.hospital_name.data,
                    "bio": form.bio.data.capitalize(),
                    "operating_hours": json.loads(form.operating_hours.data) if form.operating_hours.data else [],
                    "created_at": datetime.now(),
                }

                existing_user = get_doctor_collection().find_one({"email": form.email.data})
                if existing_user:
                    flash("This email address is already registered.", "alert-danger")
                    return render_template("signUp_doctor.html", form=form)
                
                existing_license = get_doctor_collection().find_one({"license_number": form.license_number.data})
                if existing_license:
                    flash("This license number is already registered.", "alert-danger")
                    return render_template("signUp_doctor.html", form=form)

                get_doctor_collection().insert_one(user)
                flash("You have successfully signed up!", "alert-success")
                return redirect(url_for("auth.login_doctor"))

            except Exception as e:
                flash("An error occurred during registration. Please try again.", "alert-danger")
                return redirect(url_for('auth.signUp_doctor'))
    
    return render_template("signUp_doctor.html", form=form)



@auth.route("/signup_patient", methods=["GET", "POST"])
def signUp_patient():
    form = SignUp_patient()

    if form.validate_on_submit():
        password_hash = generate_password_hash(form.password.data, method="pbkdf2:sha256")
        user = {
            "user_type": "patient",
            "first_name": form.first_name.data.capitalize(),
            "last_name": form.last_name.data.capitalize(),
            "phone": form.phone.data,
            "birth": form.birth.data.strftime('%Y-%m-%d'),
            "sex": form.sex.data,
            "insurance": form.insurance.data,
            "address": form.address.data,
            "email": form.email.data,
            "password": password_hash,
            "preferred_language": form.preferred_language.data,
            "medical_history": form.medical_history.data,
            "comments_for_doctor": form.comments_for_doctor.data,
            "created_at": datetime.now(),
        }

        existing_user = get_patient_collection().find_one({"email": form.email.data})
        if existing_user:
            flash("This email address is already registered.", "alert-danger")
            return render_template("signUp_patient.html", form=form)
        
        if form.password.data != form.confirm_password.data:
            flash('Password and confirmation do not match.', 'alert-danger')
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print("Password and confirmation do not match.")
            return render_template("signUp_patient.html", form=form)
        
        get_patient_collection().insert_one(user)

        flash("You have successfully signed up!", "alert-success")
        return redirect(url_for("auth.login_patient"))

    return render_template("signUp_patient.html", form=form)



@auth.route('/check_login')
def check_login():
    if 'user_id' not in session or 'user_type' not in session:
        return jsonify({
            'is_logged_in': False,
            'user_type': None
        })
    
    user_id = session['user_id']
    user_type = session['user_type']
    
    user_collection = get_patient_collection() if user_type == 'patient' else get_doctor_collection()
    user = user_collection.find_one({'_id': ObjectId(user_id)}) if user_collection else None
    
    if not user:
        session.clear()
        return jsonify({
            'is_logged_in': False,
            'user_type': None
        })
        
    return jsonify({
        'is_logged_in': True,
        'user_id': str(user.get('_id')),
        'user_type': user.get('user_type'),
        'user_name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
    })







@auth.route("/login/patient", methods=["GET", "POST"])
def login_patient():
    form = LoginForm()
    # 쿼리 파라미터를 세션에 저장
    if request.method == "GET":
        session['doctor_id'] = request.args.get("doctor_id")
        session['appointment_date'] = request.args.get("date")
        session['appointment_time'] = request.args.get("time")
        session['appointment_day'] = request.args.get("day")
        
    

    if form.validate_on_submit():
        user = get_patient_collection().find_one({"email": form.email.data})
        
        if user and check_password_hash(user["password"], form.password.data):
            session['user'] = user['email']
            session['user_id'] = str(user['_id'])
            session['user_type'] = 'patient'
            session['user_name'] = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            
            # 세션에서 값 가져와서 리다이렉트
            doctor_id = session.pop("doctor_id", None)
            appointment_date = session.pop("appointment_date", None)
            appointment_time = session.pop("appointment_time", None)
            appointment_day = session.pop("appointment_day", None)
            
            if doctor_id and appointment_date and appointment_time and appointment_day:
                return redirect(url_for('views.booking', doctor_id=doctor_id, date=appointment_date, day=appointment_day, time=appointment_time))
            
            flash("Patient login successful", "alert-success")
            return redirect(url_for("views.landing_page"))
        
        flash("Invalid email or password for patient.", "alert-danger")
    
    return render_template("login_patient.html", form=form)





@auth.route("/login/doctor", methods=["GET", "POST"])
def login_doctor():
    form = LoginForm()
    if form.validate_on_submit():
        user = get_doctor_collection().find_one({"email": form.email.data})
        
        if user and check_password_hash(user["password"], form.password.data):
            session['user'] = user['email']
            session['user_id'] = str(user['_id'])
            session['user_type'] = 'doctor'
            session['user_name'] = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            flash("Doctor login successful", "alert-success")
            return redirect(url_for("views.landing_page"))
        
        flash("Invalid email or password for doctor.", "alert-danger")
    
    return render_template("login_doctor.html", form=form)





@auth.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "alert-success")
    return redirect(request.referrer or url_for("views.landing_page"))