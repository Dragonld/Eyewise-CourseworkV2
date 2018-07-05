from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField,DateTimeField, SelectField,\
    IntegerField, FloatField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User
from datetime import datetime


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
        choices=[("Eye test","Eye test"), ("Contact lens check", "Contact lens check"),("Glasses fitting","Glasses fitting")])
    practice = SelectField(choices=[("Stourbridge","Stourbridge"),("Telford","Telford")], validators=[DataRequired()])
    # date_time = DateTimeField("Appointment Date and Time", validators=[])
    # date = DateField("Appointment Date", validators=[])
    year = StringField(validators=[DataRequired()], default=str(datetime.now().year))
    month = SelectField(validators=[DataRequired()], choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),
                                                              ('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),
                                                              ('11','11'),('12','12')])
    day = SelectField(validators=[DataRequired()],
                      choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),
                               ('9','9'),('10','10'),('11','11'),('12','12'),('13','13'),('14','14'),('15','15'),
                               ('16','16'),('17','17'),('18','18'),('19','19'),('20','20'),('21','21'),('22','22'),
                               ('23','23'),('24','24'),('25','25'), ('26','26'),('27','27'),('28','28'),('29','29'),
                               ('30','30'),('31','31')])
    hour = SelectField(validators=[DataRequired()],
                       choices=[('8','8'),('9','9'),('10','10'),('11','11'),('12','12'),('13','13'),('14','14'),('15','15')])
    minute = SelectField(validators=[DataRequired()], choices=[('00','00'),('30','30')])


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


class AddMissedForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    num_missed = IntegerField("Number missed", validators=[DataRequired()], default=1)
    submit = SubmitField("Submit changes")

class AddMonForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    mon_spent = FloatField("Money spent", validators=[DataRequired()])
    submit = SubmitField("Submit changes")


class ChangeRoleForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    new_role = IntegerField("Role", validators=[DataRequired()])
    submit = SubmitField("Submit changes")


class AddStockForm(FlaskForm):
    id= IntegerField("Item ID", validators=[DataRequired()])
    colour = StringField("Colour", validators=[DataRequired()])
    stock = IntegerField("Added stock", validators=[DataRequired()])
    submit = SubmitField("Add stock")


class OptomForm(FlaskForm):
    practice = SelectField(validators=[DataRequired()],
                           choices=[("Stourbridge","Stourbridge"),("Telford","Telford"), ("None","None")], default="None")
    year = IntegerField(validators=[DataRequired()], default=str(datetime.now().year))
    month = SelectField(validators=[DataRequired()],
                        choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
                                 ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'),
                                 ('11', '11'), ('12', '12')])
    day = SelectField(validators=[DataRequired()],
                      choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
                               ('8', '8'),
                               ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'),
                               ('15', '15'),
                               ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'),
                               ('22', '22'),
                               ('23', '23'), ('24', '24'), ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'),
                               ('29', '29'),
                               ('30', '30'), ('31', '31')])
    submit = SubmitField("Add date")