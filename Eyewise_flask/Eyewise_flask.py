#analysis of missed and empty appointments and profitability(appointments compared to money spent)
from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

@app.route("/")
@app.route('/home')
def home():
    user = {"username":"Richard"}
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
    return render_template("home.html", title= "Home", user=user, posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title="Information")

@app.route("/contact")
def contact():
    return render_template("contact.html", title="Contact")

@app.route("/social_media")
def Social_media():
    return render_template("Social_media.html", title="Contact")

@app.route("/where_to_find")
def where_to_find():
    return render_template("where_to_find.html", title = "Contact")

@app.route("/makeapo")
def makeapo():
    return render_template("Make an appointment.html", title="Appointment form")


if __name__ == '__main__':
    app.run()
