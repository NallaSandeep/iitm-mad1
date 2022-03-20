from flask import Flask
import os
from flask_restful import Api

from application.config import LocalDevelopmentConfig
from application.database import db
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_security import Security, SQLAlchemySessionUserDatastore, SQLAlchemyUserDatastore
from application.models import *
from flask_login import LoginManager
from flask_security import LoginForm, url_for_security


import logging

logging.basicConfig(filename='debug.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

app = None
rest_api = None

login_manager = LoginManager()


# TODO
# ● Validation - P1
# Integration of APIs with frontend app
# ○ All form inputs fields - text, numbers etc. with suitable messages
# Login dropdown not working in log create/update screens
# Breadcrumb is not displayed with format
# P3
# Timestamp - 2022-05-26T11:42:00.73+05:30 - P3
# The current timestamp needs to be picked up automatically - P3
# Format of Time of last view (Today, Yesterday or Three months ago) - P2
# Check if you can  implement auth functionality
# develop admin page for setting roles & create user


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder="static")
    if os.getenv('ENV', "development") == "production":
        app.logger.info("Currently no production config is setup.")
        raise Exception("Currently no production config is setup.")
    else:
        app.logger.info("Staring Local Development.")
        app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    login_manager.init_app(app)
    api = Api(app)
    app.app_context().push()
    # Setup Flask-Security
    user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    security = Security(app, user_datastore)
    app.logger.info("App setup complete")
    return app, api


web_app, rest_api = create_app()


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Importing web controllers
from application.controllers import *


@app.errorhandler(404)
def not_found(e):
    return redirect(url_for('not_found_page'))


@app.errorhandler(403)
def unauth(e):
    return redirect(url_for('unauth_page'))


# Importing REST API controllers
from application.api import *

rest_api.add_resource(TrackerApi, '/api/tracker', '/api/trackers/<int:tracker_id>')
rest_api.add_resource(LogApi, '/api/trackers/<int:tracker_id>/log', '/api/trackers/<int:tracker_id>/logs/<int:log_id>')
rest_api.add_resource(LogsApi, '/api/trackers/<int:tracker_id>/logs')

if __name__ == '__main__':
    web_app.run(debug=True)
