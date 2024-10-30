from flask import Blueprint, render_template, jsonify, session, flash, redirect, url_for, request
import requests
import os

from forms import *
from db import *
from datetime import datetime, timedelta
from auth import check_login

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
            "medical_school": doctor.get("medical_school"),
            "specialization": doctor.get("specialization"),
            "hospital_name": doctor.get("hospital_name"),
            "image": doctor.get("image"),
            "address": doctor.get("address"),
            "bio": doctor.get("bio"),
            "operating_hours": doctor.get("operating_hours", {}),
            "rating": avg_rating,
            "reviews": reviews,
        })

    return jsonify(doctor_list)



# @views.route("/booking", methods=["GET", "POST"])
# def booking(doctor_id):
#     form = AppointmentForm()

#     doctor = get_doctor_collection.find_one({"_id": doctor_id})
#     operating_hours = doctor.get("operating_hours", {})

#     if form.appointment_date.data:
#         select_date = form.appointment_date.data
#         weekday = select_date.strftime("%A").lower()

#         time_slots = operating_hours.get(weekday, [])

#         available_times = []
#         for time in time_slots:
#             start_time, end_time = time.split("-")
#             current_time = datetime.strftime(start_time, "%H:%M")
#             end_time = datetime.strftime(end_time, "%H:%M")

#             while current_time < end_time:
#                 available_times.append(current_time.strftime("%H:%M"))
#                 current_time += timedelta(minutes=30)

#         form.appointment_date.choices = [(time, time) for time in available_times]

#     if form.validate_on_submit():
#         appointment_data = {
#             "doctor_id": doctor_id,
#             "patient_id": session['user_id'],
#             "date": form.appointment_date.data,
#             "time": form.appointment_time.data,
            
#         }

#         existing_appointment = get_appointment_collection.find_one({
#             "doctor_id": doctor_id,
#             "date": form.appointment_date.data,
#             "time": form.appointment_time.data,
#         })

#         if existing_appointment:
#             flash("Selected time is already booked. Please choose another time.", "alert-danger")

#         else:
#             get_appointment_collection.insert_one(appointment_data)
#             get_doctor_collection.update_one(
#                 {"_id": doctor_id},
#                 {"$push": {"appointments": appointment_data}}
#             )
#             get_patient_collection.update_one(
#                 {"_id": session['user_id']},
#                 {"$push": {"appointments": appointment_data}}
#             )

#             flash("Your appointment has been booked successfully!", "alert-success")
#             return redirect(url_for(views.booking))
        
#         return render_template('booking.html', form=form, doctor=doctor)
    # user_email = session.get('user')
    # user_info = get_patient_collection().find_one({"email": user_email})
    # if not user_info:
    #     return redirect(url_for('auth.login', next=request.url))

    # if request.method == "POST":
    #     # 예약 처리 코드 (예: 예약 정보를 MongoDB에 저장)
    #     appointment_data = {
    #         "date": request.form.get("appointment_date"),
    #         "time": request.form.get("appointment_time"),
    #         "patient_email": user_email,
    #         "note": request.form.get("note"),
    #     }
    #     get_patient_collection().insert_one(appointment_data)
    #     flash("Your appointment has been booked successfully.", "success")
    #     return redirect(url_for('auth.myAccount'))

    # return render_template("book_loggedin.html", user_info=user_info)




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