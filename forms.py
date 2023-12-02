from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# WTForm for creating a cafe
class CreateCafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    map_url = StringField("Cafe Location on Google Maps (URL)", validators=[DataRequired(), URL()])
    location = StringField("Name of City", validators=[DataRequired()])
    open = StringField("Opening Time e.g: 8AM", validators=[DataRequired()])
    close = StringField("Closing Time e.g: 5:30PM", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    seats = StringField("Number Of Seats e.g: 50+ or 40-50", validators=[DataRequired()])
    toilet = BooleanField("Are Toilets Available?")
    wifi = BooleanField("Is Wifi Available?")
    sockets = BooleanField("Are There Power Sockets?")
    calls = BooleanField("Are Calls Allowed?")
    coffee_price = StringField("Coffee Price e.g: $2.5", validators=[DataRequired()])
    submit = SubmitField('Submit')

# class CreateCafeForm(FlaskForm):
#     cafe = StringField('Cafe name', validators=[DataRequired()])
#     location = StringField("Cafe Location on Google Maps (URL)", validators=[DataRequired(), URL()])
#     open = StringField("Opening Time e.g. 8AM", validators=[DataRequired()])
#     close = StringField("Closing Time e.g. 5:30PM", validators=[DataRequired()])
#     coffee_rating = SelectField("Coffee Rating", choices=["☕️", "☕☕", "☕☕☕", "☕☕☕☕", "☕☕☕☕☕"],
#                                 validators=[DataRequired()])
#     wifi_rating = SelectField("Wifi Strength Rating", choices=["✘", "💪", "💪💪", "💪💪💪", "💪💪💪💪", "💪💪💪💪💪"],
#                               validators=[DataRequired()])
#     power_rating = SelectField("Power Socket Availability", choices=["✘", "🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌", "🔌🔌🔌🔌🔌"],
#                                validators=[DataRequired()])
#     submit = SubmitField('Submit')
#     img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])



# Create a form to register new users
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign up")


# Create a form to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


# Create a form to add comments
class CommentForm(FlaskForm):
    comment_text = StringField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")

