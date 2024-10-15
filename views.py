from flask import Blueprint, render_template, jsonify
import requests
import os

from dotenv import load_dotenv
from flask_cors import CORS

views = Blueprint("views", __name__)

load_dotenv()

@views.route("/")
def landing_page():
    return render_template("index.html")

@views.route("/search")
def search():
    return render_template("MVP.html")

@views.route("/booking")
def booking():
    return render_template("book.html")

@views.route("/book_loggedin")
def login2():
    return render_template("book_loggedin.html")





CORS(views, resources={r"/api/*": {"origins": "*"}})
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