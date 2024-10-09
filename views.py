from flask import Blueprint, blueprints, render_template

views = Blueprint("view", __name__)

@views.route("/")
def landing_page():
    return render_template("index.html")

@views.route("/search")
def search():
    return render_template("MVP.html")

@views.route("/booking")
def booking():
    return render_template("book.html")

@views.route("/login")
def login():
    return render_template("login.html")

@views.route("/sign_up")
def sign_up():
    return render_template("signUp.html")

@views.route("/book_loggedin")
def login2():
    return render_template("book_loggedin.html")