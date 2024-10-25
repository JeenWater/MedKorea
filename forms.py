from tkinter import Button
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField, DateField, TextAreaField, IntegerField, SelectMultipleField
from wtforms.validators import InputRequired, Length, EqualTo, Email
import os
from dotenv import load_dotenv

load_dotenv()

class ChangePassword(FlaskForm):
    current_password = PasswordField('Current Password', validators=[InputRequired(), Length(min=6, max=20)])
    new_password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm New Password', validators=[InputRequired()])
    submit = SubmitField('Change Password')



class EditProfile_patient(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired(), Length(min=2, max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(min=2, max=30)])
    phone = StringField("Phone Number", validators=[InputRequired(), Length(min=10, max=15)])
    birth = DateField("Date of Birth", format='%Y-%m-%d', validators=[InputRequired()])
    sex = SelectField("Sex", choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])
    insurance = SelectField("Health Insurance", choices=[('y', 'Yes'), ('n', 'No')])
    address = StringField("Address", validators=[ Length(max=100)])
    preferred_language = SelectField("Preferred Language", choices=[('English', 'English'), ('Chinese', 'Chinese'), ('Japanese', 'Japanese')], validators=[])
    medical_history = TextAreaField("Medical History", validators=[])
    comments_for_doctor = TextAreaField("Comments for Doctor", validators=[])
    submit = SubmitField("Save Changes")



class SignUp_patient(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired(), Length(min=2, max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(min=2, max=30)])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password')])
    phone = StringField("Phone Number", validators=[InputRequired(), Length(min=10, max=15)])
    birth = DateField("Date of Birth", format='%Y-%m-%d', validators=[InputRequired()])
    sex = SelectField("Sex", choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])
    insurance = SelectField("Health Insurance", choices=[('y', 'Yes'), ('n', 'No')])
    preferred_language = SelectField("Preferred Language", choices=[('English', 'English'), ('Chinese', 'Chinese'), ('Japanese', 'Japanese')], validators=[])
    address = StringField("Address", validators=[InputRequired(), Length(max=100)])
    medical_history = TextAreaField("Medical History", validators=[])
    comments_for_doctor = TextAreaField("Comments for Doctor", validators=[])
    submit = SubmitField("Register")



class EditProfile_doctor(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired(), Length(min=1, max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(min=1, max=30)])
    phone = StringField("Phone Number", validators=[InputRequired(), Length(min=10, max=15)])
    birth = DateField("Date of Birth", format='%Y-%m-%d', validators=[InputRequired()])
    sex = SelectField("Sex", choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])
    address = StringField("Address", validators=[ Length(max=100)])
    preferred_language = SelectField("Preferred Language", choices=[('English', 'English'), ('Chinese', 'Chinese'), ('Japanese', 'Japanese')], validators=[])
    specialization = StringField("Specialization", validators=[InputRequired(), Length(max=100)])
    license_number = StringField("Medical License Number", validators=[InputRequired(), Length(min=6, max=10)])
    medical_school = StringField("Medical School", validators=[InputRequired(), Length(min=2, max=30)])
    graduation_year = IntegerField("Graduation Year", validators=[InputRequired()])
    bio = TextAreaField("Biography", validators=[InputRequired(), Length(max=500)])
    address = StringField("Practice Address (optional)", validators=[Length(max=100)])
    submit = SubmitField("Save Changes")
    operating_hours = StringField("Operating Hours", validators=[])
    # availability = SelectField("Availability", choices=[], validators=[InputRequired()])

    # def __init__(self, *args, **kwargs):
    #     super(EditProfile_doctor, self).__init__(*args, **kwargs)
    #     self.availability.choices = self.generate_availability_choices()

    # @staticmethod
    # def generate_availability_choices():
    #     availability_range = os.getenv('DOCTOR_AVAILABILITY', '09:00-17:00')
    #     start_time, end_time = map(lambda x: int(x.split(":")[0]), availability_range.split('-'))
    #     choices = []
    #     for hour in range(start_time, end_time):
    #         for minute in [0, 30]:
    #             time_str = f"{hour:02d}:{minute:02d}"
    #             display_str = f"{hour % 12 or 12}:{minute:02d} {'AM' if hour < 12 else 'PM'} - " \
    #                           f"{(hour % 12 + 1) % 12 or 12}:{minute:02d} {'AM' if (hour + 1) < 12 else 'PM'}"
    #             choices.append((time_str, display_str))
    #     return choices



class SignUp_doctor(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired(), Length(min=1, max=20)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(min=1, max=20)])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password')])
    phone = StringField("Phone Number", validators=[InputRequired(), Length(min=10, max=15)])
    birth = DateField("Date of Birth", format='%Y-%m-%d', validators=[InputRequired()])
    sex = SelectField("Sex", choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])
    preferred_language = SelectField("Preferred Language", choices=[('English', 'English'), ('Chinese', 'Chinese'), ('Japanese', 'Japanese')], validators=[])
    specialization = StringField("Specialization", validators=[InputRequired(), Length(max=100)])
    license_number = StringField("Medical License Number", validators=[InputRequired(), Length(min=8, max=10)])
    medical_school = StringField("Medical School", validators=[InputRequired(), Length(min=2, max=30)])
    graduation_year = IntegerField("Graduation Year", validators=[InputRequired()])
    bio = TextAreaField("Biography", validators=[InputRequired(), Length(max=500)])
    address = StringField("Practice Address (optional)", validators=[Length(max=100)])
    operating_hours = StringField("Operating Hours", validators=[])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=20)])
    submit = SubmitField("Login")