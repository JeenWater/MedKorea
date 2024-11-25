from flask import Blueprint, render_template, jsonify, session, flash, redirect, url_for, request
import requests
import os

from forms import AppointmentForm
from db import get_patient_collection, get_doctor_collection
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





@views.route("/booking", methods=["GET", "POST"])
def booking():
    form = AppointmentForm()

    doctor = None
    user_id = session.get("user_id")
    doctor_id = request.args.get("doctor_id") or request.form.get("doctor_id")
    date = request.args.get("date") or request.form.get("appointment_date")
    time = request.args.get("time") or request.form.get("appointment_time")
    day = request.args.get("day") or request.form.get("appointment_day")
    user = get_patient_collection().find_one({"_id": ObjectId(user_id)})

    if doctor_id:
        doctor = get_doctor_collection().find_one({"_id": ObjectId(doctor_id)})

    if request.method == 'GET':
        if not user_id:
            flash("Please log in first.", "alert-danger")
            return redirect(url_for("auth.login_patient", doctor_id=doctor_id, date=date, time=time))

        user = get_patient_collection().find_one({"_id": ObjectId(user_id)})
        if not doctor:
            flash("Doctor not found", "alert-danger")
            return redirect(url_for("views.search"))

        return render_template("booking.html", doctor=doctor, user=user, form=form, appointment_date=date, appointment_time=time, appointment_day=day)

    if request.method == 'POST':
        if not doctor:
            flash("Doctor not found", "alert-danger")
            return redirect(url_for("views.search"))

        try:
            first_name = form.first_name.data or user['first_name']
            last_name = form.last_name.data or user['last_name']
            phone = form.phone.data or user['phone']
            birth = form.birth.data or user['birth']
            sex = form.sex.data or user['sex']
            insurance = form.insurance.data or user['insurance']
            email = form.email.data or user['email']
            medical_history = form.medical_history.data or user['medical_history']
            comments_for_doctor = form.comments_for_doctor.data or user['comments_for_doctor']
            preferred_language = form.preferred_language.data or user['preferred_language']

            birth = form.birth.data.strftime('%Y-%m-%d') if form.birth.data else user['birth'].strftime('%Y-%m-%d')

            get_patient_collection().update_one(
                {"_id": ObjectId(user_id)},
                {"$push": 
                    {"appointments": {
                        "date": date,
                        "time": time,
                        "day": day,
                        "doctor_id": doctor_id,
                        "doctor_name": f"Dr. {doctor['first_name']} {doctor['last_name']}",
                        "status": "scheduled",
                        "created_at": datetime.now()
                        }
                    }
                }
            )

            get_doctor_collection().update_one(
                {"_id": ObjectId(doctor_id)},
                {"$push": 
                    {"appointments": {
                        "date": date,
                        "time": time,
                        "day": day,
                        "patient_id": user_id,
                        "patient_name": f"{first_name} {last_name}",
                        "first_visit": form.first_visit.data,
                        "phone": phone,
                        "birth": birth,
                        "sex": sex,
                        "insurance": insurance,
                        "preferred_language": preferred_language,
                        "email": email,
                        "medical_history": medical_history,
                        "comments_for_doctor": comments_for_doctor,
                        "status": "scheduled",
                        "created_at": datetime.now()
                        }
                    }
                }
            )
            
            flash("Appointment booked successfully.", "alert-success")
            return redirect(url_for("views.landing_page"))
        
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            flash('An error occurred. Please try again later.', 'alert-danger')

    return render_template("booking.html", doctor=doctor, user=user, form=form, appointment_date=date, appointment_time=time, appointment_day=day)









@views.route("/cancel_appointment", methods=["POST"])
def cancel_appointment():
    data = request.get_json()
    appointment_id = data["appointment_id"]
    cancel_reason = data["cancel_reason"]

    user_id = session.get("user_id")
    user_type = session.get("user_type")
    collection = get_patient_collection() if user_type == "patient" else get_doctor_collection()

    result = collection.update_one(
        {"_id": ObjectId(user_id), "appointments._id": ObjectId(appointment_id)},
        {"$set": {
            "appointments.$.status": "cancelled",
            "appointments.$.cancel_reason": cancel_reason,
            "appointments.$.cancelled_at": datetime.now()
        }}
    )
    if result.modified_count > 0:
        send_email_notification(user_id, "Your appointment has been cancelled.")
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})





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