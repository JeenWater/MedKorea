import re
from wtforms.validators import ValidationError
from flask import flash

def password_strength_check(form, field):
    password = field.data
    if not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) \
    or not re.search(r'\d', password) or not re.search(r'[@$!%*?&#]', password):
        flash("Password must contain uppercase, lowercase, number, and special character.", "alert-danger")
        raise ValidationError("Password must contain uppercase, lowercase, number, and special character.")