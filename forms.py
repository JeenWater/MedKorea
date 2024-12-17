from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, SubmitField, EmailField, SelectField, DateField, TextAreaField, IntegerField, TimeField
from wtforms.validators import InputRequired, Length, Email, ValidationError
from flask_wtf.file import FileField, FileRequired
from datetime import datetime, timedelta
from dotenv import load_dotenv
from validators import password_strength_check

load_dotenv()










class SearchDoctorsForm(FlaskForm):
    condition = StringField("Condition", validators=[Length(min=2, max=30)])
    location = StringField("Location", validators=[Length(max=100)])
    date = DateField("Select Date", format='%Y-%m-%d', validators=[InputRequired()])
    submit = SubmitField("Search")






class AppointmentForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired(), Length(min=1, max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(min=1, max=30)])
    first_visit = SelectField("Is this your first visit?", choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])
    phone = StringField("Phone Number", validators=[InputRequired(), Length(min=10, max=15)])
    birth = DateField("Date of Birth", format='%Y-%m-%d', validators=[InputRequired()])
    sex = SelectField("Sex", choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])
    preferred_language = SelectField("Preferred Language", choices=[('English', 'English'), ('Chinese', 'Chinese'), ('Japanese', 'Japanese')])
    insurance = SelectField("Health Insurance", choices=[('y', 'Yes'), ('n', 'No')])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    medical_history = TextAreaField("Medical History")
    comments_for_doctor = TextAreaField("Comments for Doctor")
    submit = SubmitField("Book Appointment")

    appointment_date = DateField("Select Date", format='%Y-%m-%d', validators=[InputRequired()])
    appointment_time = TimeField("Select Time", format='%H:%M:%S', validators=[InputRequired()])
    appointment_day = StringField("Day of the Week", validators=[InputRequired()])



class VerifyEmail(FlaskForm):
    email = EmailField("Email", validators=[InputRequired(), Email()])
    code = StringField("Verification Code", validators=[InputRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify')




class ChangePassword(FlaskForm):
    current_password = PasswordField('Current Password', validators=[InputRequired(), Length(min=6, max=20)])
    new_password = PasswordField("New Password", validators=[InputRequired(), Length(min=6, max=20), password_strength_check])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired()])
    submit = SubmitField('Change Password')



class EditProfile_patient(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired(), Length(min=1, max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(min=1, max=30)])
    phone = StringField("Phone Number", validators=[InputRequired(), Length(min=10, max=15)])
    birth = DateField("Date of Birth", format='%Y-%m-%d', validators=[InputRequired()])
    sex = SelectField("Sex", choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])
    insurance = SelectField("Health Insurance", choices=[('y', 'Yes'), ('n', 'No')])
    preferred_language = SelectField("Preferred Language", choices=[('English', 'English'), ('Chinese', 'Chinese'), ('Japanese', 'Japanese')], validators=[])
    address = StringField("Address", validators=[ Length(max=100)])
    medical_history = TextAreaField("Medical History", validators=[])
    comments_for_doctor = TextAreaField("Comments for Doctor", validators=[])
    submit = SubmitField("Save Changes")



class SignUp_patient(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired(), Length(min=1, max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(min=1, max=30)])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=20), password_strength_check])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired()])
    phone = StringField("Phone Number", validators=[InputRequired(), Length(min=10, max=15)])
    birth = DateField("Date of Birth", format='%Y-%m-%d', validators=[InputRequired()])
    sex = SelectField("Sex", choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])
    insurance = SelectField("Health Insurance", choices=[('n', 'No'), ('y', 'Yes')])
    preferred_language = SelectField("Preferred Language", choices=[('English', 'English'), ('Chinese', 'Chinese'), ('Japanese', 'Japanese')], validators=[])
    address = StringField("Address", validators=[InputRequired(), Length(max=100)])
    medical_history = TextAreaField("Medical History", validators=[])
    comments_for_doctor = TextAreaField("Comments for Doctor", validators=[])
    submit = SubmitField("Register")



class EditProfile_doctor(FlaskForm):
    image = FileField("Profile Picture", validators=[FileRequired()])
    first_name = StringField("First Name", validators=[InputRequired(), Length(min=1, max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(min=1, max=30)])
    phone = StringField("Phone Number", validators=[InputRequired(), Length(min=10, max=15)])
    birth = DateField("Date of Birth", format='%Y-%m-%d', validators=[InputRequired()])
    sex = SelectField("Sex", choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])
    address = StringField("Address", validators=[ Length(max=100)])
    preferred_language = SelectField("Preferred Language", choices=[('English', 'English'), ('Chinese', 'Chinese'), ('Japanese', 'Japanese')], validators=[])
    specialty = StringField("Specialization", validators=[InputRequired(), Length(max=100)])
    license_number = StringField("Medical License Number", validators=[InputRequired(), Length(min=6, max=10)])
    medical_school = StringField("Medical School", validators=[InputRequired(), Length(min=2, max=50)])
    graduation_year = IntegerField("Graduation Year", validators=[InputRequired()])
    bio = TextAreaField("Biography", validators=[InputRequired(), Length(max=500)])
    address = StringField("Practice Address (optional)", validators=[Length(max=100)])
    hospital_name = StringField("Practice Address", validators=[Length(min=1, max=50)])
    submit = SubmitField("Save Changes")
    operating_hours = StringField("Operating Hours", validators=[])



class SignUp_doctor(FlaskForm):
    image = FileField("Profile Picture", validators=[FileRequired()])
    first_name = StringField("First Name", validators=[InputRequired(), Length(min=1, max=20)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(min=1, max=20)])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=20), password_strength_check])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired()])
    phone = StringField("Phone Number", validators=[InputRequired(), Length(min=10, max=15)])
    birth = DateField("Date of Birth", format='%Y-%m-%d', validators=[InputRequired()])
    sex = SelectField("Sex", choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])
    preferred_language = SelectField("Preferred Language", choices=[('English', 'English'), ('Chinese', 'Chinese'), ('Japanese', 'Japanese')], validators=[])
    specialty = StringField("Specialization", validators=[InputRequired(), Length(max=100)])
    license_number = StringField("Medical License Number", validators=[InputRequired(), Length(min=8, max=10)])
    medical_school = StringField("Medical School", validators=[InputRequired(), Length(min=2, max=50)])
    graduation_year = IntegerField("Graduation Year", validators=[InputRequired()])
    bio = TextAreaField("Biography", validators=[InputRequired(), Length(max=500)])
    address = StringField("Practice Address", validators=[Length(max=100)])
    hospital_name = StringField("Practice Address", validators=[Length(min=1, max=50)])
    operating_hours = StringField("Operating Hours", validators=[])
    submit = SubmitField("Register")



class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=20)])
    submit = SubmitField("Login")