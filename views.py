from flask import Blueprint, render_template, jsonify, session, flash, redirect, url_for, request, current_app
from flask_mail import Message
from pymongo import DESCENDING
import requests
import os
from flask_mail import Message, Mail

from forms import AppointmentForm, SearchDoctorsForm
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
    user_status = session.get('user_status')
    if user_status:
        session.clear()
    session['today'] = datetime.today().strftime('%Y-%m-%d')

    return render_template("index.html")






@views.route("/search", methods=["GET", "POST"])
def mvp():
    form = SearchDoctorsForm()
    today = datetime.today().strftime('%Y-%m-%d')
    page = int(request.args.get('page', 1))
    # 한 페이지에 보여줄 의사 수
    per_page = 3

    condition = request.args.get("condition")
    location = request.args.get("location")
    date = request.args.get("date") or today

    filter = {"user_type": "doctor"}

    if condition:
        # condition filtering
        filter["$or"] = [
            {"first_name": {"$regex": condition, "$options": "i"}},
            {"last_name": {"$regex": condition, "$options": "i"}},
            {"hospital_name": {"$regex": condition, "$options": "i"}},  # hospital name
            {"specialty": {"$regex": condition, "$options": "i"}},  # specialty
            {"bio": {"$regex": condition, "$options": "i"}}  # bio
        ]

    if location:
        # location filtering
        filter["address"] = {"$regex": location, "$options": "i"}

    doctors = get_doctor_collection().find(filter)
    doctors_availabilities = []

    for doctor in doctors:
        doctor_id = str(doctor["_id"])

        booked_appointments = get_appointment_collection().find({
            "doctor_id": doctor_id,
            "status": "upcoming"
        })
        # date = datetime.strptime(date, '%b %d %Y').strftime('%Y-%m-%d')
        # time = datetime.strptime(time, '%I:%M %p').strftime('%H:%M:%S')
        booked_times = [
                {"date": appt["appointment_date"], "time": appt["appointment_time"]} for appt in booked_appointments
            ]

        # review and rating
        reviews = doctor.get("reviews", [])
        avg_rating = sum([review["rating"] for review in reviews]) / len(reviews) if reviews else None
        
        # available time
        available_times = get_available_times_for_doctor(doctor, date, booked_times)

        # print(available_times[0]['availableTimes'][0]['time'])
        
        doctors_availabilities.append({
            "id": doctor_id,
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
            "booked_times": booked_times,
            "available_times": available_times
        })
    doctors_availabilities = [
        doctor for doctor in doctors_availabilities if doctor["available_times"]
    ]

    total_doctors = len(doctors_availabilities)
    total_pages = (total_doctors // per_page) + (1 if total_doctors % per_page > 0 else 0)

    page = max(1, min(page, total_pages))

    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    doctors_list = doctors_availabilities[start_index:end_index]

    return render_template("MVP.html", doctors=doctors_list, form=form, page=page, total_pages=total_pages, condition=condition, location=location, date=date)



def get_available_times_for_doctor(doctor, date, booked_times):
    available_dates = []
    selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    operating_hours = doctor.get('operating_hours', {})  # get doctor's operating hours (start & end time for the each day)

    for i in range(4):  # appears 4 days
        # from today or inserted date
        next_date = selected_date + timedelta(days=i)
        day_of_week = next_date.strftime('%A')  # day: Monday
        date_str = next_date.strftime("%Y-%m-%d") # date: 2024-12-10
        is_today = (next_date == datetime.today().date())

        # get start & end time for the each day from operating hours
        if day_of_week in operating_hours:
            start_time_str = operating_hours[day_of_week]['start']
            end_time_str = operating_hours[day_of_week]['end']

            # generate available times
            available_times = get_available_times(start_time_str, end_time_str, date_str, day_of_week, is_today)

            # exclude booked times
            filtered_available_times = [
                time for time in available_times
                if not any(
                    booked["date"] == date_str and booked["time"] == time["time"]
                    for booked in booked_times
                )
            ]

            for i in range(len(filtered_available_times)):
                time = filtered_available_times[i]['time']
                time = datetime.strptime(time, "%H:%M:%S").strftime('%I:%M %p')
                filtered_available_times[i]['time'] = time

            # return filtered_available_times
            if filtered_available_times:
                available_dates.append({
                    'date': datetime.strptime(date_str, '%Y-%m-%d').strftime('%b %d %Y'),
                    'availableTimes': filtered_available_times,
                    'day': day_of_week,
                    'isToday': is_today
                })

    return available_dates



def get_available_times(start, end, date, day, isToday=False):
    times = []

    # make start and end of the day
    current_time = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")

    # make a current time
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    
    while current_time <= end_time:
        hour = current_time.hour
        minute = current_time.minute
        
        # pass the past time
        if isToday and datetime.strptime(date, "%Y-%m-%d").date() == datetime.today().date():
            if hour < current_hour or (hour == current_hour and minute <= current_minute):
                current_time += timedelta(minutes=30)
                continue

        # pass for lunch time ect.
        if day != 'Saturday' and (hour == 13 or (hour == 14 and minute == 0)):
            current_time += timedelta(minutes=30)
            continue

        # if the hospital works over 2pm, break
        if day == 'Saturday' and hour >= 14:
            break

        times.append({
            'date': date,
            'time': current_time.strftime("%H:%M:%S"),
            'day': day
        })
        
        current_time += timedelta(minutes=30)

    return times









@views.route("/booking", methods=["GET", "POST"])
def booking():
    form = AppointmentForm()

    user_id = session.get("user_id")
    doctor_id = request.args.get("doctor_id") or request.form.get("doctor_id")
    # get date data as '%b %d %Y', '%I:%M %p' formation('Nov 28 2024', '09:00 AM', 'Thursday')
    date = request.args.get("date") or request.form.get("appointment_date")
    time = request.args.get("time") or request.form.get("appointment_time")
    day = request.args.get("day") or request.form.get("appointment_day")
    user = get_patient_collection().find_one({"_id": ObjectId(user_id)})

    today = datetime.today().date()

    try:
        # string object to datetime object
        appointment_date = datetime.strptime(date, "%b %d %Y").date()
    except ValueError:
        flash("Invalid date format.", "alert-danger")
        return redirect(url_for("views.mvp"))
    
    if appointment_date < today:
        flash("You cannot schedule an appointment in the past.", "alert-danger")
        return redirect(url_for("views.mvp"))


    if not doctor_id:
        flash("Doctor ID is missing.", "alert-danger")
        return redirect(url_for("views.mvp"))

    doctor = get_doctor_collection().find_one({"_id": ObjectId(doctor_id)})

    if not doctor:
        flash("Doctor not found.", "alert-danger")
        return redirect(url_for("views.mvp"))

    if request.method == 'GET':
        if not user_id:
            flash("Please log in first.", "alert-danger")
            return redirect(url_for("auth.login_patient", doctor_id=doctor_id, date=date, time=time, day=day))

        return render_template("booking.html", doctor=doctor, user=user, form=form, appointment_date=date, appointment_time=time, appointment_day=day)

    if request.method == 'POST':
        # and alter these codes' formats to '%Y-%m-%d' and '%H:%M:%S'('2024-11-28', '09:00:00') for db
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
            return redirect(url_for("views.mvp"))

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
                return redirect(url_for("views.mvp"))
            
            # send an email
            subject_patient = "Appointment Confirmation"
            body_patient = (
                f"Dear {first_name} {last_name},\n\n"
                f"Your appointment with Dr. {doctor['first_name']} {doctor['last_name']} "
                f"has been successfully booked.\n\n"
                f"Date: {date}\nTime: {time}\nDay: {day}\n\n"
                f"Thank you for using MedKorea.\n\n"
                f"Best regards,\nThe MedKorea Team"
            )

            # to a patient
            email_sent_patient = send_email(email, subject_patient, body_patient)

            if not email_sent_patient:
                flash("Appointment booked, but failed to send confirmation email to patient.", "alert-warning")

            # to a doctor
            subject_doctor = "New Appointment Confirmation"
            body_doctor = (
                f"Dear Dr. {doctor['first_name']} {doctor['last_name']},\n\n"
                f"You have a new appointment with {first_name} {last_name}.\n\n"
                f"Patient Details:\n"
                f"Name: {first_name} {last_name}\n"
                f"Phone: {phone}\n"
                f"Email: {email}\n\n"
                f"Appointment Details:\n"
                f"Date: {date}\nTime: {time}\nDay: {day}\n\n"
                f"Thank you for using MedKorea.\n\n"
                f"Best regards,\nThe MedKorea Team"
            )

            email_sent_doctor = send_email(doctor['email'], subject_doctor, body_doctor)

            if not email_sent_doctor:
                flash("Appointment booked, but failed to send confirmation email to the doctor.", "alert-warning")

            flash("Appointment booked successfully. Confirmation email has been sent.", "alert-success")
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
        date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        page = int(request.args.get('page', 1))
        per_page = 3 if user_type == 'patient' else 4

        query = {"patient_id": user_id} if user_type == 'patient' else {"doctor_id": user_id}
        appointments = list(
            get_appointment_collection().find(query).sort(
                [("appointment_date", DESCENDING), ("appointment_time", DESCENDING)]
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

        total_past_appointments = len(past_appointments)
        total_pages = (total_past_appointments // per_page) + (1 if total_past_appointments % per_page > 0 else 0)
        
        past_appointments_paginated = past_appointments[(page - 1) * per_page : page * per_page]

        for appt in upcoming_appointments + past_appointments:
            appt['appointment_date'] = appt['full_appt_time'].strftime('%b %d %Y')
            appt['appointment_time'] = appt['full_appt_time'].strftime('%I:%M %p')

        return render_template(
            "myAppointments.html",
            upcoming_appointments=upcoming_appointments,
            past_appointments=past_appointments_paginated,
            user_type=user_type,
            page=page,
            total_pages=total_pages,
            date_filter=date_filter
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
    day = request.args.get('day')

    existing_appointment = get_appointment_collection().find_one({
        "doctor_id": doctor_id,
        "appointment_date": date,
        "appointment_time": time,
        "status": "upcoming"
    })

    if existing_appointment:
        return jsonify({"success": False, "message": "The selected time is already booked."})

    return jsonify({"success": True})



@views.route("/myappointments/cancel", methods=["POST"])
def cancel_appointment():
    appointment_id = request.json.get('appointment_id') if request.json.get('appointment_id') else "67615ed5d8027ab285d935ac"
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
        email = ''

        # update the doctor's booked_times by removing the canceled appointment time
        get_doctor_collection().update_one(
            {"_id": ObjectId(appt['doctor_id'])},
            {"$pull": {"booked_times": {"date": appt['appointment_date'], "time": appt['appointment_time']}}}
        )

        # send an email to a patient
        email = appt['email']
        subject_patient = "Cancellation Confirmation"
        body_patient = (
            f"Dear {appt['patient_name']},\n\n"
            f"Your appointment with {appt['doctor_name']} "
            f"has been successfully canceled.\n\n"
            f"Date: {appt['appointment_date']}\nTime: {appt['appointment_time']}\nDay: {appt['appointment_day']}\n\n"
            f"Thank you for using MedKorea.\n\n"
            f"Best regards,\nThe MedKorea Team"
        )
        email_sent_patient = send_email(email, subject_patient, body_patient)
        if not email_sent_patient:
                print("Appointment canceled, but failed to send confirmation email to the patient.", "alert-warning")

        # send an email to a doctor
        doctor = get_doctor_collection().find_one({"_id": ObjectId(appt['doctor_id'])})
        email = doctor['email']
        subject_doctor = "Cancellation Confirmation"
        body_doctor = (
            f"Dear {doctor['first_name']} {doctor['last_name']},\n\n"
            f"Your appointment with {appt['patient_name']} "
            f"has been successfully canceled.\n\n"
            f"Date: {appt['appointment_date']}\nTime: {appt['appointment_time']}\nDay: {appt['appointment_day']}\n\n"
            f"Thank you for using MedKorea.\n\n"
            f"Best regards,\nThe MedKorea Team"
        )
        email_sent_doctor = send_email(email, subject_doctor, body_doctor)
        if not email_sent_doctor:
                print("Appointment canceled, but failed to send confirmation email to the doctor.", "alert-warning")

    if result.matched_count:
        flash("Appointment canceled successfully. Confirmation email has been sent.", "alert-success")
        return jsonify({"success": True}), 200
    else:
        return flash("Failed to cancel the appointment. Please try again.", "alert-danger")










def send_email(recipient, subject, body):
    import main
    mail = main.mail
    msg = Message(subject, recipients=[recipient], body=body)
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False





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