@echo off
set FLASK_APP=Eyewise_flask.py
set MAIL_SERVER=localhost
set MAIL_PORT=8025
flask db init
flask db migrate
flask db upgrade