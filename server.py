from os import environ
from flask import Flask

app = Flask(__name__)
app.run(environ.get('PORT'))
# These are used to purely satisfy heroku app to prevent it being reported as crash state. However, the main script are run by the Advanced Scheduler to trigger YMCA_booking.py
# Inspired by https://stackoverflow.com/questions/39139165/running-simple-python-script-continuously-on-heroku