"""Forms for main application"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    """University system login form"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login to University System')

class StudentSearchForm(FlaskForm):
    """Student search form"""
    search = StringField('Search Students', validators=[Length(max=100)])
    submit = SubmitField('Search')
