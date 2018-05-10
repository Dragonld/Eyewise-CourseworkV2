from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField, DateTimeField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User
# from datetime import datetime


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class MakeAppointmentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    appointment_type = SelectField(
        validators=[DataRequired()],
        choices=[("eye_test","Eye test"), ("contact_check", "Contact lens check"),("glasses_fit","Glasses fit")])
    practice = SelectField(choices=[("stourbridge","Stourbridge"),("telford","Telford")], validators=[DataRequired()])
    #date_time = DateTimeField("Appointment Date and Time", validators=[DataRequired()], format=['%Y-%m-%d %H:%M'])

    submit = SubmitField('Book Appointment')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address1 = StringField("Address 1", validators=[])
    address2 = StringField("Address 2", validators=[])
    town_city = StringField("Town/City", validators=[])
    postcode = StringField("Postcode", validators=[])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    admin = 0
    telephone_num = StringField("Telephone number", validators=[])

    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telephone_num = StringField("Telephone number", validators=[DataRequired])
    address1 = StringField("Address 1")
    address2 = StringField("Address 2")
    town_city = StringField("Town/City")
    postcode = StringField("Postcode")
    submit = SubmitField('Submit')

    def __init__(self, original_username, original_email,  *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            if username.data.startswith("Admin"):
                raise ValidationError('Please use a different username.')
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired()])
    new_password2 = PasswordField('Repeat new password', validators=[DataRequired(), EqualTo("new_password")])
    old_password = PasswordField('Old password', validators=[DataRequired()])
    submit = SubmitField("Confirm change")

