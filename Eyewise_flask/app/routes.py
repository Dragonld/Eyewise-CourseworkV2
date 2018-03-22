from app import app
from app.forms import MakeAppointmentForm
from flask import render_template, url_for, redirect


@app.route("/")
@app.route('/home')
def home():
    user = {"username": "Richard"}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("home.html", title="Home", user=user, posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title="Information")


@app.route("/contact")
def contact():
    return render_template("contact.html", title="Contact")


@app.route("/contact/social_media")
def social_media():
    return render_template("social_media.html", title="Contact")


@app.route("/contact/where_to_find")
def where_to_find():
    return render_template("where_to_find.html", title="Contact")


@app.route("/make_appointment", methods=['GET', 'POST'])
def make_appointment():
    form = MakeAppointmentForm()
    if form.validate_on_submit():
        # Put code here to add the appointment to the database
        print('First name :: {}\nLast name :: {}\nemail :: {}'.format(form.first_name.data, form.last_name.data, form.email.data))
        return redirect(url_for('home'))
    return render_template("make_appointment.html", title="Appointment form", form=form)
