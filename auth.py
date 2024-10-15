from flask import Blueprint, request, render_template, redirect, url_for, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import certifi
from forms import SignUp_patient, LoginForm

auth = Blueprint("auth", __name__)

load_dotenv()

client = MongoClient(os.getenv('MONGO_URI'), tlsCAFile=certifi.where())
db = client['users']
patients_collection = db['patient']

@auth.route("/signUp_patient", methods=["GET", "POST"])
def signUp_patient():
    form = SignUp_patient()
    
    if form.validate_on_submit():
        password_hash = generate_password_hash(form.password.data, method="pbkdf2:sha256")
        user = {
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "email": form.email.data,
            "password": password_hash,
            "phone": form.phone.data,
            "birth": str(form.birth.data),
            "sex": form.sex.data,
            "insurance": form.insurance.data,
            "user_type": "patient",
        }
        
        existing_user = patients_collection.find_one({"email": form.email.data})
        if existing_user:
            flash("This email address is already registered.", "danger")
            return redirect(url_for('auth.signUp_patient'))

        patients_collection.insert_one(user)

        flash("You have successfully signed up!", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("signUp_patient.html", form=form)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = patients_collection.find_one({"email": form.email.data})

        if user and check_password_hash(user["password"], form.password.data):
            flash("Login successful", "success")
            return redirect(url_for("views.home"))
        
        else:
            flash("Login unsuccessful", "danger")
            return redirect(url_for("auth.login"))
        
    return render_template("login.html", form=form)
