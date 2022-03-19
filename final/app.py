from flask import Flask
import os
from flask_restful import Api

from application.config import LocalDevelopmentConfig
from application.database import db

app = None
rest_api = None


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


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder="static")
    if os.getenv('ENV', "development") == "production":
        raise Exception("Currently no production config is setup.")
    else:
        print("Staring Local Development")
        app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api = Api(app)
    app.app_context().push()
    return app, api


web_app, rest_api = create_app()

# Importing web controllers
from application.controllers import *

# Importing REST API controllers
from application.api import *

rest_api.add_resource(TrackerApi, '/api/tracker', '/api/trackers/<int:tracker_id>')
rest_api.add_resource(LogApi, '/api/trackers/<int:tracker_id>/log', '/api/trackers/<int:tracker_id>/logs/<int:log_id>')
rest_api.add_resource(LogsApi, '/api/trackers/<int:tracker_id>/logs')

if __name__ == '__main__':
    web_app.run(debug=True)
