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
from flask_security import RegisterForm
from wtforms import StringField
from wtforms.validators import DataRequired


import logging

logging.basicConfig(filename='debug.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

app = None
rest_api = None


class ExtendedRegisterForm(RegisterForm):
    username = StringField('User Name', [DataRequired()])


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder="static")
    if os.getenv('ENV', "development") == "production":
        app.logger.info("Currently no production config is setup.")
        raise Exception("Currently no production config is setup.")
    else:
        app.logger.info("Staring Local Development.")
        app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api = Api(app)
    app.app_context().push()
    # Setup Flask-Security
    user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    security = Security(app, user_datastore, register_form=ExtendedRegisterForm)
    app.logger.info("App setup complete")
    return app, api


web_app, rest_api = create_app()


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

rest_api.add_resource(TrackerApi, '/api/trackers', '/api/trackers/<int:tracker_id>')
rest_api.add_resource(LogApi, '/api/trackers/<int:tracker_id>/log', '/api/trackers/<int:tracker_id>/logs/<int:log_id>')
rest_api.add_resource(LogsApi, '/api/trackers/<int:tracker_id>/logs')

if __name__ == '__main__':
    web_app.run(debug=True)
