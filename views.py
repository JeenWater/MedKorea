from flask import Blueprint, render_template, jsonify, session, flash, redirect, url_for, request
import requests
import os

from forms import AppointmentForm
from db import get_patient_collection, get_doctor_collection, get_appointment_collection
from datetime import datetime, timedelta
from bson.objectid import ObjectId

from dotenv import load_dotenv
from flask_cors import CORS

views = Blueprint("views", __name__)

CORS(views, resources={r"/api/*": {"origins": "*"}})

load_dotenv()





@views.route("/")
def landing_page():
    print()
    return render_template("index.html")





@views.route("/search")
def search():
    return render_template("MVP.html")





@views.route("/api/doctors")
def get_doctors():
    doctors = get_doctor_collection().find({"user_type": 'doctor'})

    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 3))

    doctor_list = []
    for doctor in doctors.skip(offset).limit(limit):
        reviews = doctor.get("reviews", [])
        avg_rating = sum([review["rating"] for review in reviews]) / len(reviews) if reviews else None
        
        doctor_list.append({
            "id": str(doctor["_id"]),
            "first_name": doctor.get("first_name"),
            "last_name": doctor.get("last_name"),
            "phone": doctor.get("phone"),
            "preferred_language": doctor.get("preferred_language"),
            "medical_school": doctor.get("medical_school"),
            "specialty": doctor.get("specialty"),
            "hospital_name": doctor.get("hospital_name"),
            "image": doctor.get("image"),
            "address": doctor.get("address"),
            "bio": doctor.get("bio"),
            "operating_hours": doctor.get("operating_hours", {}),
            "rating": avg_rating,
            "reviews": reviews,
        })

    return jsonify(doctor_list)










@views.route("/booking", methods=["GET", "POST"])
def booking():
    form = AppointmentForm()

    user_id = session.get("user_id")
    doctor_id = request.args.get("doctor_id") or request.form.get("doctor_id")
    date = request.args.get("date") or request.form.get("appointment_date")
    time = request.args.get("time") or request.form.get("appointment_time")
    day = request.args.get("day") or request.form.get("appointment_day")
    user = get_patient_collection().find_one({"_id": ObjectId(user_id)})
    print(date, time, day)

    if not doctor_id:
        flash("Doctor ID is missing.", "alert-danger")
        return redirect(url_for("views.search"))
    
    doctor = get_doctor_collection().find_one({"_id": ObjectId(doctor_id)})
    if not doctor:
        flash("Doctor not found.", "alert-danger")
        return redirect(url_for("views.search"))

    if request.method == 'GET':
        if not user_id:
            flash("Please log in first.", "alert-danger")
            return redirect(url_for("auth.login_patient", doctor_id=doctor_id, date=date, time=time))

        return render_template("booking.html", doctor=doctor, user=user, form=form, appointment_date=date, appointment_time=time, appointment_day=day)

    if request.method == 'POST':
        try:
            first_name = form.first_name.data or user['first_name']
            last_name = form.last_name.data or user['last_name']
            phone = form.phone.data or user['phone']
            birth = form.birth.data.strftime('%Y-%m-%d') if form.birth.data else user['birth']
            sex = form.sex.data or user['sex']
            insurance = form.insurance.data or user['insurance']
            email = form.email.data or user['email']
            medical_history = form.medical_history.data or user['medical_history']
            comments_for_doctor = form.comments_for_doctor.data or user['comments_for_doctor']
            preferred_language = form.preferred_language.data or user['preferred_language']

            get_appointment_collection().insert_one({
                "doctor_id": doctor_id,
                "doctor_name": f"Dr. {doctor['first_name']} {doctor['last_name']}",
                "patient_id": user_id,
                "patient_name": f"{first_name} {last_name}",
                "appointment_date": date,
                "appointment_time": time,
                "appointment_day": day,
                "phone": phone,
                "birth": birth,
                "sex": sex,
                "insurance": insurance,
                "email": email,
                "medical_history": medical_history,
                "comments_for_doctor": comments_for_doctor,
                "preferred_language": preferred_language,
                "status": "upcoming",
                "first_visit": form.first_visit.data,
                "created_at": datetime.now()
            })
            
            flash("Appointment booked successfully.", "alert-success")
            return redirect(url_for("views.landing_page"))

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            flash('An error occurred. Please try again later.', 'alert-danger')

    return render_template("booking.html", doctor=doctor, user=user, form=form, appointment_date=date, appointment_time=time, appointment_day=day)










# @views.route("/myappointments")
# def appointments():
#     """View all appointments for the logged-in patient."""
#     user_email = session.get("user")
#     user_type = session.get("user_type")

#     print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
#     print(user_email)
#     print(user_type)
#     print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

#     if not user_email:
#         flash("Please log in to view your appointments.", "alert-danger")
#         return redirect(url_for("views.landing_page"))

#     appointments = []
#     if user_type == "patient":
#         appointments = list(get_appointment_collection().find({"email": user_email}))

#     elif user_type == "doctor":
#         doctor_id = session.get("doctor_id")
#         appointments = list(get_appointment_collection().find({"doctor_id": doctor_id}))
    
#     print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
#     print(appointments)
#     print(user_type)
#     print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

#     return render_template("myAppointments.html", appointments=appointments, user_type=user_type)





@views.route("/myappointments", methods=["GET"])
def appointments():
    user_id = session.get('user_id')
    user_type = session.get('user_type')

    if not user_id:
        flash("Please log in to view your appointment history.", "alert-danger")
        return redirect(url_for("views.landing_page"))
    
    appointments = []
    if user_type == 'patient':
        appointments = list(get_appointment_collection().find({"patient_id": user_id}))
    elif user_type == 'doctor':
        appointments = list(get_appointment_collection().find({"doctor_id": user_id}))

    # 의사 정보 캐싱 딕셔너리
    doctor_cache = {}

    # 예약 데이터에 의사 정보 추가
    for appt in appointments:
        doctor_id = appt.get('doctor_id')
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(get_doctor_collection().find_one({"_id": ObjectId(doctor_id)}))
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        if doctor_id and doctor_id not in doctor_cache:
            doctor_info = get_doctor_collection().find_one({"_id": ObjectId(doctor_id)})
            if doctor_info:
                doctor_cache[doctor_id] = {
                    "name": f"Dr. {doctor_info.get('first_name')} {doctor_info.get('last_name')}",
                    "image": doctor_info.get('image', 'default.png'),
                    "specialty": doctor_info.get('specialty'),
                    "hospital_name": doctor_info.get('hospital_name', 'N/A'),
                    "address": doctor_info.get('address', 'N/A'),
                    "bio": doctor_info.get('bio', 'N/A'),
                    "languages": doctor_info.get('languages', ['English'])
                }
        
        # 예약 데이터에 의사 정보 추가
        appt['doctor_info'] = doctor_cache.get(doctor_id, {})

    print("\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print(appt)
    # print(appointments[0]['doctor_id'])
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

    upcoming_appointments = [
        appt for appt in appointments if appt['status'] == 'upcoming'
    ]
    past_appointments = [
        appt for appt in appointments if appt['status'] in ['completed', 'canceled']
    ]

    # upcoming_appointments = list(get_appointment_collection().find({
    #     "patient_id": user_id,
    #     "status": "upcoming"
    # }).sort("appointment_date", 1))

    # past_appointments = list(get_appointment_collection().find({
    #     "patient_id": user_id,
    #     "status": {"$in": ["completed", "canceled"]}
    # }).sort("appointment_date", -1))

    return render_template("myAppointments.html",
                        upcoming_appointments=upcoming_appointments, 
                        past_appointments=past_appointments,
                        user_type=user_type
                        )





@views.route("/myappointment/edit/<appointment_id>", methods=["GET", "POST"])
def edit_appointment(appointment_id):
    """Edit an existing appointment."""
    user_email = session.get("user")
    if not user_email:
        flash("Please log in to manage your appointments.", "alert-danger")
        return redirect(url_for("auth.login_patient"))

    appointment = get_appointment_collection().find_one({"_id": ObjectId(appointment_id)})
    if not appointment:
        flash("Appointment not found.", "alert-danger")
        return redirect(url_for("views.myAppointments"))

    form = AppointmentForm()

    date = form.appointment_date.data or appointment.get("appointment_date")
    time = form.appointment_time.data or appointment.get("appointment_time")
    day = form.appointment_day.data or appointment.get("appointment_day")

    if request.method == "GET":
        # Pre-fill the form with existing appointment data
        from_user_data(form, appointment)

        return render_template("edit_appointment.html", form=form, appointment=appointment)

    if request.method == "POST":
        first_name = form.first_name.data or appointment.get('first_name')
        last_name = form.last_name.data or appointment.get('last_name')
        phone = form.phone.data or appointment.get('phone')
        birth = form.birth.data.strftime('%Y-%m-%d') if form.birth.data else appointment.get('birth')
        sex = form.sex.data or appointment.get('sex')
        insurance = form.insurance.data or appointment.get('insurance')
        email = form.email.data or appointment.get('email')
        medical_history = form.medical_history.data or appointment.get('medical_history')
        comments_for_doctor = form.comments_for_doctor.data or appointment.get('comments_for_doctor')
        preferred_language = form.preferred_language.data or appointment.get('preferred_language')

        try:
            # Update the appointment in the database
            updated_data = {
                "patient_name": f"{first_name} {last_name}",
                "appointment_date": date,
                "appointment_time": time,
                "appointment_day": day,
                "phone": phone,
                "birth": birth,
                "sex": sex,
                "insurance": insurance,
                "email": email,
                "medical_history": medical_history,
                "comments_for_doctor": comments_for_doctor,
                "preferred_language": preferred_language,
                "status": "upcoming", # upcoming, completed, canceled
                "first_visit": form.first_visit.data,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
                # "appointment_date": form.appointment_date.data,
                # "appointment_time": form.appointment_time.data,
                # "comments_for_doctor": form.comments_for_doctor.data,
                # "status": "updated",
            }

            get_appointment_collection().update_one(
                {"_id": ObjectId(appointment_id)},
                {"$set": updated_data}
            )
            
            if result.modified_count > 0:
                flash("Appointment updated successfully.", "alert-success")
            else:
                flash("Failed to update appointment. Please try again.", "alert-danger")

            return redirect(url_for("views.myAppointments"))

        except Exception as e:
            print(f"Error occurred while updating appointment: {str(e)}")
            flash("An error occurred. Please try again later.", "alert-danger")

    return render_template("edit_appointment.html", form=form, appointment=appointment)



def from_user_data(form, appointment):
    form.first_name.data = appointment.get('first_name')
    form.last_name.data = appointment.get('last_name')
    form.phone.data = appointment.get('phone')
    form.birth.data = datetime.strptime(appointment['birth'], '%Y-%m-%d')
    form.sex.data = appointment.get('sex')
    form.preferred_language.data = appointment.get('preferred_language')
    form.insurance.data = appointment.get('insurance')
    form.address.data = appointment.get('address')
    form.medical_history.data = appointment.get('medical_history')
    form.comments_for_doctor.data = appointment.get('comments_for_doctor')





@views.route("/myappointment/cancel/<appointment_id>", methods=["POST"])
def cancel_appointment(appointment_id):
    cancel_reason = request.json.get('reason', '')

    result = get_appointment_collection().update_one(
        {"_id": ObjectId(appointment_id)},
        {"$set": {
            "status": "canceled",
            "cancel_reason": cancel_reason,
            "updated_at": datetime.now()
            }
        }
    )

    if result.modified_count > 0:
        flash("Appointment canceled successfully.", "alert-success")
    else:
        flash("Failed to cancel appointment. Please try again.", "alert-danger")

    return redirect(url_for("views.myAppointments"))






def send_email_notification(user_id, message):
    user = get_patient_collection().find_one({"_id": ObjectId(user_id)})
    if user:
        email = user.get("email")
        print(f"Email sent to {email}: {message}")





NEWS_API_KEY = os.getenv('NEWS_API_KEY')

@views.route('/api/health-news', methods=['GET'])
def get_health_news():
    url = f'https://newsapi.org/v2/everything?q=health&apiKey={NEWS_API_KEY}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return jsonify(data['articles'])
    else:
        return jsonify({"error": "Unable to fetch data"}), 500