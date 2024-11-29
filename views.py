from flask import Blueprint, render_template, jsonify, session, flash, redirect, url_for, request
from pymongo import ASCENDING
import requests
import os

from forms import AppointmentForm, Edit_AppointmentForm
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
    return render_template("index.html")





@views.route("/search")
def search():
    return render_template("MVP.html")




# for doctors on MVP page 
@views.route("/api/doctors")
def get_doctors():
    doctors = get_doctor_collection().find({"user_type": 'doctor'})

    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 3))

    doctor_list = []
    for doctor in doctors.skip(offset).limit(limit):


        doctor_id = str(doctor['_id'])

        booked_appointments = get_appointment_collection().find({
            "doctor_id": doctor_id,
            "status": "upcoming"
        })

        booked_times = []

        for appt in booked_appointments:
            date = datetime.strptime(appt["appointment_date"], '%Y-%m-%d').strftime('%b %d %Y')
            time = datetime.strptime(appt["appointment_time"], '%H:%M:%S').strftime('%I:%M %p')
            booked_times = [
                {
                    "date": date,
                    "time": time
                }
            ]

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
            "booked_times": booked_times
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
            return redirect(url_for("auth.login_patient", doctor_id=doctor_id, date=date, time=time, day=day))

        return render_template("booking.html", doctor=doctor, user=user, form=form, appointment_date=date, appointment_time=time, appointment_day=day)

    if request.method == 'POST':
        date = datetime.strptime(date, '%b %d %Y').strftime('%Y-%m-%d')
        time = datetime.strptime(time, '%I:%M %p').strftime('%H:%M:%S')
        # prevent to trip stacking
        existing_appointment = get_appointment_collection().find_one({
            "doctor_id": doctor_id,
            "appointment_date": date,
            "appointment_time": time,
            "status": "upcoming"
        })

        if existing_appointment:
            flash("This time slot is no longer available. Please choose another time.", "alert-danger")
            return redirect(url_for("views.search"))

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

            result = get_appointment_collection().insert_one({
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
                "status": "upcoming", # upcoming, completed, cancelled
                "first_visit": form.first_visit.data,
                "created_at": datetime.now()
            })

            get_doctor_collection().update_one(
                {"_id": ObjectId(doctor_id)},
                {
                    "$push": {
                        "booked_times": {
                            "date": date,
                            "time": time
                        }
                    }
                }
            )

            if result.inserted_id is None:
                flash("Failed to book appointment. Please try again.", "alert-danger")
                return redirect(url_for("views.search"))

            flash("Appointment booked successfully.", "alert-success")
            return redirect(url_for("views.landing_page"))

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            flash('An error occurred. Please try again later.', 'alert-danger')

    return render_template("booking.html", doctor=doctor, user=user, form=form, appointment_date=date, appointment_time=time, appointment_day=day)
















@views.route("/myappointments", methods=["GET", "POST"])
def appointments():
    user_id = session.get('user_id')
    user_type = session.get('user_type')

    if not user_id:
        flash("Please log in to view your appointment history.", "alert-danger")
        return redirect(url_for("views.landing_page"))

    try:
        
        query = {"patient_id": user_id} if user_type == 'patient' else {"doctor_id": user_id}
        appointments = list(
            get_appointment_collection().find(query).sort(
                [("appointment_date", ASCENDING), ("appointment_time", ASCENDING)]
            )
        )

        # update status
        current_date = datetime.now()

        for appt in appointments:
            appt_date = appt.get('appointment_date')
            appt_time = appt.get('appointment_time')

            if isinstance(appt_date, str):
                appt_date = datetime.strptime(appt_date, '%Y-%m-%d')
            if isinstance(appt_time, str):
                appt_time = datetime.strptime(appt_time, '%H:%M:%S').time()

            # combine date and time correctly
            if appt_date and appt_time:
                full_appt_time = datetime.combine(appt_date, appt_time)
                appt['full_appt_time'] = full_appt_time

                if full_appt_time < current_date and appt['status'] == 'upcoming':
                    # 1. update the status to completed
                    get_appointment_collection().update_one(
                        {"_id": appt['_id']}, {"$set": {"status": "completed"}}
                    )

                    # 2. delete the same time in booked_times in doctor's db
                    get_doctor_collection().update_one(
                        {"_id": ObjectId(appt['doctor_id'])},
                        {"$pull": {"booked_times": {"date": appt['appointment_date'], "time": appt['appointment_time']}}}
                    )
                    appt['status'] = "completed"

        appointments.sort(key=lambda x: x['full_appt_time'])

        # caching the list
        doctor_cache = {}
        for appt in appointments:
            doctor_id = appt.get('doctor_id')
            if doctor_id and doctor_id not in doctor_cache:
                doctor_info = get_doctor_collection().find_one({"_id": ObjectId(doctor_id)})
                doctor_cache[doctor_id] = doctor_info or {}
            appt['doctor_info'] = doctor_cache.get(doctor_id, {})

        # sort the list
        upcoming_appointments = [appt for appt in appointments if appt['status'] == 'upcoming']
        past_appointments = [appt for appt in appointments if appt['status'] in ['completed', 'canceled']]

        past_appointments.sort(key=lambda x: x['full_appt_time'], reverse=True)

        for appt in upcoming_appointments + past_appointments:
            appt['appointment_date'] = appt['full_appt_time'].strftime('%b %d %Y')
            appt['appointment_time'] = appt['full_appt_time'].strftime('%I:%M %p')

        return render_template(
            "myAppointments.html",
            upcoming_appointments=upcoming_appointments,
            past_appointments=past_appointments,
            user_type=user_type
        )

    except Exception as e:
        print(f"Error in appointments route: {e}")
        flash("An error occurred while loading appointments.", "alert-danger")
        return redirect(url_for("views.landing_page"))




# check if the selected date and time are already booked
@views.route('/myappointments/check-availability', methods=['POST'])
def check_availability():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    date = datetime.strptime(data.get('date'), '%Y-%m-%d').strftime('%b %d %Y')
    time = datetime.strptime(data.get('time'), '%H:%M:%S').strftime('%I:%M %p')

    existing_appointment = get_appointment_collection().find_one({
        "doctor_id": doctor_id,
        "appointment_date": date,
        "appointment_time": time,
        "status": "upcoming"
    })

    if existing_appointment:
        return jsonify({"success": False, "message": "The selected time is already booked."})

    return jsonify({"success": True})



# edit the appointment with the new date and time
@views.route('/myappointments/edit', methods=['POST'])
def edit_appointment():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    appointment_id = data.get('appointment_id')
    new_date = datetime.strptime(data.get('new_date'), '%Y-%m-%d').strftime('%b %d %Y')
    new_time = datetime.strptime(data.get('new_time'), '%H:%M:%S').strftime('%I:%M %p')

    existing_appointment = get_appointment_collection().find_one({
        "_id": ObjectId(appointment_id),
        "doctor_id": doctor_id,
        "status": "upcoming"
    })

    if existing_appointment:
        result = get_appointment_collection().update_one(
            {"_id": ObjectId(appointment_id)},
            {
                "$set": {
                    "appointment_date": new_date,
                    "appointment_time": new_time
                }
            }
        )

        get_doctor_collection().update_one(
                {"_id": ObjectId(doctor_id)},
                {
                    "$push": {
                        "booked_times": {
                            "date": new_date,
                            "time": new_time
                        }
                    }
                }
            )

        if result.modified_count == 1:
            flash("Appointment updated successfully.", "alert-success")
            return jsonify({"success": True})
        else:
            flash("Failed to update appointment.", "alert-danger")
            return jsonify({"success": False, "message": "Update failed."})
    else:
        flash("Appointment not found.", "alert-danger")
        return jsonify({"success": False, "message": "Appointment not found."})






@views.route("/myappointments/cancel", methods=["POST"])
def cancel_appointment():
    appointment_id = request.json.get('appointment_id')
    cancel_reason = request.json.get('cancel_reason')

    if not appointment_id:
        return flash("Appointment cancellation failed. Invalid appointment ID.", "alert-danger")

    if not cancel_reason.strip():
        return flash("Cancellation reason is required to cancel an appointment.", "alert-danger")

    # update appointment status in the db
    result = get_appointment_collection().update_one(
        {"_id": ObjectId(appointment_id)},
        {"$set": {"status": "canceled", "cancel_reason": cancel_reason}}
    )

    if result.modified_count > 0:
        # retrieve the appointment details
        appt = get_appointment_collection().find_one({"_id": ObjectId(appointment_id)})

        # update the doctor's booked_times by removing the canceled appointment time
        get_doctor_collection().update_one(
            {"_id": ObjectId(appt['doctor_id'])},
            {"$pull": {"booked_times": {"date": appt['appointment_date'], "time": appt['appointment_time']}}}
        )

    if result.matched_count:
        flash("Appointment canceled successfully.", "alert-success")
        return jsonify({"success": True}), 200
    else:
        return flash("Failed to cancel the appointment. Please try again.", "alert-danger")











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