from flask import Flask
from dotenv import load_dotenv
import os

from views import views
from auth import auth



load_dotenv()

app = Flask(__name__)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')

app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/auth')



if __name__ == "__main__":
    app.run(debug=True, port=9119)