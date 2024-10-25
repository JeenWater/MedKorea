from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify, json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from db import get_patient_collection, get_doctor_collection
from forms import SignUp_patient, LoginForm, EditProfile_patient, ChangePassword, SignUp_doctor, EditProfile_doctor
from bson.objectid import ObjectId


auth = Blueprint("auth", __name__)

load_dotenv()



# @auth.route("/booking", methods=["GET", "POST"])
# def booking():
#     user_email = session.get('user')
#     user_info = get_patient_collection().find_one({"email": user_email})
#     if not user_info:
#         return redirect(url_for('auth.login', next=request.url))

#     if request.method == "POST":
#         # 예약 처리 코드 (예: 예약 정보를 MongoDB에 저장)
#         appointment_data = {
#             "date": request.form.get("appointment_date"),
#             "time": request.form.get("appointment_time"),
#             "patient_email": user_email,
#             "note": request.form.get("note"),
#         }
#         get_patient_collection().insert_one(appointment_data)
#         flash("Your appointment has been booked successfully.", "success")
#         return redirect(url_for('auth.myAccount'))

#     return render_template("book_loggedin.html", user_info=user_info)



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
            return redirect(url_for('auth.login_security'))

        if form.new_password.data != form.confirm_password.data:
            flash('New password and confirmation do not match.', 'alert-danger')
            return redirect(url_for('auth.login_security'))

        new_password_hash = generate_password_hash(form.new_password.data, method="pbkdf2:sha256")

        # Fixing the assignment to user
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

    if user_type == 'patient':
        user = get_patient_collection().find_one({"email": user_email})
        form = EditProfile_patient()
    elif user_type == 'doctor':
        user = get_doctor_collection().find_one({"email": user_email})
        form = EditProfile_doctor()

    if not user:
        flash("Your account was not found. Please log in again or contact support.", "alert-danger")
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        from_user_data(form, user)

    if form and form.validate_on_submit():
        update_data = {
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "phone": form.phone.data,
            "birth": form.birth.data.strftime('%Y-%m-%d'),
            "sex": form.sex.data,
            "preferred_language": form.preferred_language.data,
        }
        if user_type == 'patient':
            update_data.update({
                "insurance": form.insurance.data,
                "address": form.address.data,
                "medical_history": form.medical_history.data,
                "comments_for_doctor": form.comments_for_doctor.data,
                "updated_at": datetime.now(),
            })
        elif user_type == 'doctor':
            update_data.update({
                "medical_school": form.medical_school.data,
                "specialization": form.specialization.data,
                "graduation_year": form.graduation_year.data,
                "license_number": form.license_number.data,
                "address": form.address.data,
                "bio": form.bio.data,
                "operating_hours": json.loads(form.operating_hours.data),
                # "availability": form.availability.data,
                "updated_at": datetime.now(),
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
        form.specialization.data = user.get('specialization')
        form.license_number.data = user.get('license_number')
        form.medical_school.data = user.get('medical_school')
        form.graduation_year.data = user.get('graduation_year')
        form.address.data = user.get('address')
        form.bio.data = user.get('bio')
        operating_hours = user.get('operating_hours')
        form.operating_hours.data = json.dumps(operating_hours) if operating_hours else ''
        # form.availability.data = user.get('availability')



@auth.route("/signup_doctor", methods=["GET", "POST"])
def signUp_doctor():
    form = SignUp_doctor()
    
    if form.validate_on_submit():
        try:
            password_hash = generate_password_hash(form.password.data, method="pbkdf2:sha256")
            user = {
                "user_type": "doctor",
                "first_name": form.first_name.data,
                "last_name": form.last_name.data,
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
                "bio": form.bio.data,
                "operating_hours": json.loads(form.operating_hours.data),
                "created_at": datetime.now(),
            }

            existing_user = get_doctor_collection().find_one({"email": form.email.data})
            if existing_user:
                print("Duplicate email found")
                flash("This email address is already registered.", "alert-danger")
                return redirect(url_for('auth.signUp_doctor'))
            
            existing_license = get_doctor_collection().find_one({"license_number": form.license_number.data})
            if existing_license:
                print("Duplicate license found")
                flash("This license number is already registered.", "alert-danger")
                return redirect(url_for('auth.signUp_doctor'))
            
            if form.password.data != form.confirm_password.data:
                flash('Password and confirmation do not match.', 'alert-danger')
                return redirect(url_for('auth.signUp_doctor'))

            get_doctor_collection().insert_one(user)
            

            flash("You have successfully signed up!", "alert-success")
            return redirect(url_for("auth.login"))

        except Exception as e:
            print("=== Error occurred ===")
            print("Error type:", type(e))
            print("Error message:", str(e))
            print("Error details:", e)
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
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
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
            return redirect(url_for('auth.signUp_patient'))
        
        if form.password.data != form.confirm_password.data:
            flash('Password and confirmation do not match.', 'alert-danger')
            return redirect(url_for('auth.signUp_patient'))
        
        get_patient_collection().insert_one(user)

        flash("You have successfully signed up!", "alert-success")
        return redirect(url_for("auth.login"))

    return render_template("signUp_patient.html", form=form)



@auth.route('/check_login')
def check_login():
    if 'user' not in session:
        return jsonify({
            'is_logged_in': False,
            'user_type': None
        })
    
    user_id = session['user'].get('_id')
    user = get_patient_collection.find_one({'_id': ObjectId(user_id)})
    
    if not user:
        session.clear()
        return jsonify({
            'is_logged_in': False,
            'user_type': None
        })
        
    return jsonify({
        'is_logged_in': True,
        'user_type': user.get('user_type'),
        'user_name': user.get('name'),
        'user_id': str(user.get('_id'))
    })





@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = get_patient_collection().find_one({"email": form.email.data})
        if not user:
            user = get_doctor_collection().find_one({"email": form.email.data})
        
        if user:
            if check_password_hash(user["password"], form.password.data):
                session['user'] = user['email']
                session['user_type'] = user['user_type']
                flash("Login successful", "alert-success")
                
                if user['user_type'] == 'doctor':
                    return redirect(url_for("views.landing_page"))
                else:
                    return redirect(url_for("views.landing_page"))
            else:
                flash("Incorrect password.", "alert-danger")
        else:
            flash("User not found.", "alert-danger")

        return redirect(url_for("auth.login"))

    return render_template("login.html", form=form)



@auth.route("/logout")
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "alert-success")
    return redirect(url_for("views.landing_page"))