from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField, DateField
from wtforms.validators import InputRequired, Length, EqualTo, Email


class SignUp_patient(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired(), Length(min=2, max=20)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(min=2, max=20)])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password')])
    phone = StringField("Phone Number", validators=[InputRequired(), Length(min=10, max=15)])
    birth = DateField("Date of Birth", format='%Y-%m-%d', validators=[InputRequired()])
    sex = SelectField("Sex", choices=[('Male', 'Male'), ('Female', 'Female')], validators=[InputRequired()])
    insurance = SelectField("Health Insurance", choices=[('y', 'Yes'), ('n', 'No')])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=2, max=20)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=20)])
    submit = SubmitField("Register")