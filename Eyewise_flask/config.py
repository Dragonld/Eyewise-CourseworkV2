import os
import smtplib
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    SPOTIFY_ID = "8200001dc049483a9eee57b477832451"
    SPOTIFY_SECRET= "e88026aa9a494f7f949bc1d473406f32"

    # server = smtplib.SMTP('smtp.gmail.com', 587)
    # server.starttls()
    # server.login("YOUR EMAIL ADDRESS", "YOUR PASSWORD") #TODO Add email stuff


