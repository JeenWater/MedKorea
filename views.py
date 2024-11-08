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

    # GET 요청 처리
    if request.method == 'GET':
        print("@@@@@@@@@@@@@@@@@@@@@@@@ GET 요청 @@@@@@@@@@@@@@@@@@@@@@@@")
        print("GET\n")
        doctor = None  # doctor 변수를 먼저 초기화
        user_id = session.get("user_id")
        doctor_id = request.args.get("doctor_id") or request.form.get("doctor_id")  # GET이나 POST에서 doctor_id 가져오기
        date = request.args.get("date") or request.form.get("appointment_date")
        time = request.args.get("time") or request.form.get("appointment_time")
        
        if not user_id:
            flash("Please log in first.", "alert-danger")
            return redirect(url_for("auth.login_patient", doctor_id=doctor_id, date=date, time=time))

        # 환자 정보 조회
        user = get_patient_collection().find_one({"_id": ObjectId(user_id)})
        print("@@@@@@@@@@@@@@@@@@@@@@@@ 환자 정보 요청 @@@@@@@@@@@@@@@@@@@@@@@@")
        print(user, "\n")

        # 의사 데이터 조회
        
        if doctor_id:
            doctor = get_doctor_collection().find_one({"_id": ObjectId(doctor_id)})
        print("@@@@@@@@@@@@@@@@@@@@@@@@ Doctor 정보 요청 @@@@@@@@@@@@@@@@@@@@@@@@")
        print(doctor, "\n")
        
        if not doctor:
            flash("Doctor not found", "alert-danger")
            return redirect(url_for("views.search"))
        
        # GET 요청 시 렌더링할 데이터를 미리 준비
        return render_template("book_loggedin.html", doctor=doctor, user=user, form=form, appointment_date=date, appointment_time=time)

    # POST 요청 처리 (예약 처리)
    if request.method == 'POST' and form.validate_on_submit():
        doctor = None
        print("@@@@@@@@@@@@@@@@@@@@@@@@ POST 요청 @@@@@@@@@@@@@@@@@@@@@@@@")
        print("POST\n")
        user_id = session.get("user_id")
        doctor_id = request.form.get("doctor_id")
        date = request.form.get("appointment_date")
        time = request.form.get("appointment_time")

        # 환자 정보 조회
        user = get_patient_collection().find_one({"_id": ObjectId(user_id)})
        print("@@@@@@@@@@@@@@@@@@@@@@@@ 환자 정보 요청 @@@@@@@@@@@@@@@@@@@@@@@@")
        print(user, "\n")

        # 의사 데이터 조회
        if doctor_id:
            doctor = get_doctor_collection().find_one({"_id": ObjectId(doctor_id)})
        print("@@@@@@@@@@@@@@@@@@@@@@@@ Doctor 정보 요청 @@@@@@@@@@@@@@@@@@@@@@@@")
        print(doctor, "\n")
        
        if not doctor:
            flash("Doctor not found", "alert-danger")
            return redirect(url_for("views.search"))

        try:
            print("@@@@@@@@@@@@@@@@@@@@@@@@ SUBMIT 요청 @@@@@@@@@@@@@@@@@@@@@@@@")
            print("Submit\n")
            first_name = form.first_name.data if form.first_name.data else user['first_name']
            last_name = form.last_name.data if form.last_name.data else user['last_name']
            phone = form.phone.data if form.phone.data else user['phone']
            birth = form.birth.data if form.birth.data else user['birth']
            sex = form.sex.data if form.sex.data else user['sex']
            insurance = form.insurance.data if form.insurance.data else user['insurance']
            email = form.email.data if form.email.data else user['email']
            medical_history = form.medical_history.data if form.medical_history.data else user['medical_history']
            comments_for_doctor = form.comments_for_doctor.data if form.comments_for_doctor.data else user['comments_for_doctor']
            preferred_language = form.preferred_language.data if form.preferred_language.data else user['preferred_language']
            
            # 예약 데이터 수집
            appointment_data = {
                "date": date,
                "time": time,
                "doctor_id": doctor_id,
                "doctor_name": f"Dr. {doctor['first_name']} {doctor['last_name']}",
                "status": "scheduled",
                "created_at": datetime.now()
            }
            print("@@@@@@@@@@@@@@@@@@@@@@@@ 예약 데이터 수집 @@@@@@@@@@@@@@@@@@@@@@@@")
            print(appointment_data, "\n")

            # 1. 환자의 예약 목록에 추가
            get_patient_collection().update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"appointments": appointment_data}}
            )

            # 2. 의사의 예약 목록에 환자의 예약 정보 추가
            doctor_appointment_data = {
                "date": date,
                "time": time,
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
            print("@@@@@@@@@@@@@@@@@@@@@@@@ 의사의 예약 목록 수집 @@@@@@@@@@@@@@@@@@@@@@@@")
            print(doctor_appointment_data, "\n")
            
            get_doctor_collection().update_one(
                {"_id": ObjectId(doctor_id)},
                {"$push": {"appointments": doctor_appointment_data}}
            )
            
            flash("Appointment booked successfully.", "alert-success")
            return redirect(url_for("view.landing_page"))
        
        except Exception as e:
            views.logger.error(f"Error occurred while processing booking: {e}")
            flash('An error occurred. Please try again later.', 'danger')
            return render_template("book_loggedin.html", doctor=doctor, user=user, form=form, appointment_date=date, appointment_time=time)

    # POST 요청 시 처리되지 않는 경우는 렌더링
    return render_template("book_loggedin.html", doctor=doctor, user=user, form=form, appointment_date=date, appointment_time=time)









@views.route("/cancel_appointment", methods=["POST"])
def cancel_appointment():
    data = request.get_json()
    appointment_id = data["appointment_id"]
    cancel_reason = data["cancel_reason"]

    user_id = session.get("user_id")
    user_type = session.get("user_type")
    collection = get_patient_collection() if user_type == "patient" else get_doctor_collection()

    # 데이터베이스에서 예약 상태 업데이트
    result = collection.update_one(
        {"_id": ObjectId(user_id), "appointments._id": ObjectId(appointment_id)},
        {"$set": {
            "appointments.$.status": "cancelled",
            "appointments.$.cancel_reason": cancel_reason,
            "appointments.$.cancelled_at": datetime.now()
        }}
    )
    # 취소 상태 업데이트 후 사용자에게 알림
    if result.modified_count > 0:
        # 여기에서 이메일 또는 SMS 알림 기능 호출 (예: send_email_notification 함수)
        send_email_notification(user_id, "Your appointment has been cancelled.")
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})





def send_email_notification(user_id, message):
    # 실제 이메일 또는 SMS 알림 전송 코드
    user = get_patient_collection().find_one({"_id": ObjectId(user_id)})
    if user:
        email = user.get("email")
        # email 전송 코드 (SMTP 또는 외부 API 사용)
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