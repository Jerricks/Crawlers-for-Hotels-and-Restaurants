from flask import Flask
from flask_login import LoginManager
from flask_compress import Compress
from logging.handlers import RotatingFileHandler
from logging import Formatter
import logging

compress = Compress()  # initialize the log handler


def start():
    app = Flask(__name__)
    compress.init_app(app=app)
    return app


app = start()
app.config.from_object('config')
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

# initialize the log handler
logHandler = RotatingFileHandler('My log.log', maxBytes=1000, backupCount=1)

# set the log handler level
logHandler.setLevel(logging.INFO)

logHandler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))

# set the app logger level
app.logger.setLevel(logging.INFO)

app.logger.addHandler(logHandler)

from app import views
