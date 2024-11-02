from flask import Blueprint, render_template, jsonify, session, flash, redirect, url_for, request
import requests
import os

from forms import *
from db import get_patient_collection, get_doctor_collection
from datetime import datetime, timedelta
from auth import check_login
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
    user = None
    user_id = session.get('user_id')

    if user_id:
        user = get_patient_collection().find_one({"_id": ObjectId(user_id)})
        form = AppointmentForm()

    doctor_id = request.args.get("doctorId")
    
    if doctor_id:
        doctor = get_doctor_collection().find_one({"_id": ObjectId(doctor_id)})

    else:
        flash("Doctor ID is missing or invalid", "alert-danger")
        return redirect(url_for("views.search"))

    appointment_date = request.args.get("date")
    appointment_time = request.args.get("time")

    if doctor:
        return render_template(
            "book_loggedin.html",
            doctor=doctor,
            user=user,
            form=form,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
        )
    else:
        flash("Doctor not found", "alert-danger")
        return redirect(url_for("views.search"))




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