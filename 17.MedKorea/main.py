from flask import Flask

from flask_cors import CORS
from dotenv import load_dotenv

from views import views

app = Flask(__name__)
app.register_blueprint(views)

load_dotenv()
CORS(app, resources={r"/api/*": {"origins": "*"}})

if __name__ == "__main__":
    app.run(debug=True, port=9119)