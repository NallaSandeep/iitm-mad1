from flask import Flask, render_template, request, redirect, url_for, make_response
import os
from flask_restful import Api, Resource, fields, marshal_with, reqparse
from flask_restful.representations import json
from werkzeug.exceptions import HTTPException

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

import json

app = None
api = None
db = SQLAlchemy()

# TODO
# ● Validation - P1
# Integration of APIs with frontend app
# ○ All form inputs fields - text, numbers etc. with suitable messages
#
# P3
# Timestamp - 2022-05-26T11:42:00.73+05:30 - P3
# The current timestamp needs to be picked up automatically - P3
# Format of Time of last view (Today, Yesterday or Three months ago) - P2
# Bootstrap usage - P3
# Separate out models, controllers
# Check if you can  implement auth functionality


def create_app():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, template_folder='templates', static_folder="static")
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, 'tracker-db.db')
    db.init_app(app)
    api = Api(app)
    app.app_context().push()
    return app, api


app, api = create_app()


class User(db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)


class Tracker(db.Model):
    __tablename__ = 'tracker'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    settings = db.Column(db.String)


class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.String, nullable=False)
    tracker = db.Column(db.Integer, db.ForeignKey('tracker.id'), nullable=False)
    value = db.Column(db.String, nullable=False)
    note = db.Column(db.String)


tracker_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'type': fields.String,
    'settings': fields.String
}

log_fields = {
    'id': fields.Integer,
    'timestamp': fields.String,
    'tracker': fields.Integer,
    'value': fields.String,
    'note': fields.String
}

create_tracking_parser = reqparse.RequestParser()
create_tracking_parser.add_argument('name')
create_tracking_parser.add_argument('description')
create_tracking_parser.add_argument('type')
create_tracking_parser.add_argument('settings')

create_log_parser = reqparse.RequestParser()
create_log_parser.add_argument('timestamp')
create_log_parser.add_argument('tracker')
create_log_parser.add_argument('value')
create_log_parser.add_argument('note')


class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        error_json = {"error_code": error_code, 'error_message': error_message}
        self.response = make_response(json.dumps(error_json), status_code)


class InputValidationError(HTTPException):
    def __init__(self, status_code, error_message):
        self.response = make_response(error_message, status_code)

@app.route("/")
def home():
    return render_template('home.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.form:
        username=request.form['user-name']
        password=request.form['password']
        missing=User.query.filter_by(username=username).first()
        if missing is None:
            return redirect(url_for('login'))
        else:
            resp = make_response(redirect(url_for('trackers_page')))
            resp.set_cookie('username', username)
            return resp
    return render_template('login.html')


@app.route("/tracker")
def trackers_page():
    username = request.cookies.get('username')
    latest_logs = db.session.query(
        Log.tracker, db.func.max(Log.timestamp).label('last_tracked')
    ).group_by(Log.tracker).subquery()
    trackers = db.session.query(Tracker.id, Tracker.name, latest_logs.c.last_tracked).outerjoin(latest_logs, Tracker.id ==
                                                                               latest_logs.c.tracker)
    return render_template('trackers.html', username=username, trackers=trackers)


@app.route("/tracker/create", methods=["GET", "POST"])
def trackers_create():
    username = request.cookies.get('username')
    if request.method == 'GET':
        return render_template('tracker-create.html', username=username)
    elif request.method=='POST':
        name=request.form['name']
        desc=request.form['desc']
        type=request.form['type']
        settings=request.form['settings']
        s = Tracker(name=name, description=desc, type=type, settings=settings)
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('trackers_page'))


@app.route("/tracker/<string:tracker_id>/update", methods=["GET", "POST"])
def trackers_update(tracker_id):
    username = request.cookies.get('username')
    if request.method == 'GET':
        tracker = Tracker.query.filter_by(id=tracker_id).first()
        return render_template('tracker-update.html', username=username, tracker=tracker)
    elif request.method=='POST':
        name=request.form['name']
        desc=request.form['desc']
        type=request.form['type']
        settings=request.form['settings']
        s = Tracker.query.filter_by(id=tracker_id).update(dict(name=name, description=desc, type=type, settings=settings))
        db.session.commit()
        return redirect(url_for('trackers_page'))


@app.route("/tracker/<string:tracker_id>/delete")
def trackers_delete(tracker_id):
    Tracker.query.filter_by(id=tracker_id).delete()
    Log.query.filter_by(tracker=tracker_id).delete()
    db.session.commit()
    return redirect(url_for('trackers_page'))


@app.route("/tracker/<string:tracker_id>")
def tracker_details_page(tracker_id):
    last_days = int(request.args.get('lastdays',30))
    filter_after = datetime.today() - timedelta(days=last_days)
    username = request.cookies.get('username')
    tracker = Tracker.query.filter_by(id=tracker_id).first()
    logs = Log.query.filter_by(tracker=tracker_id).filter(Log.timestamp >= filter_after).order_by(Log.timestamp).all()
    timestamps=[]
    values=[]
    for log in logs:
        timestamps.append(log.timestamp)
        values.append(log.value)
    return render_template('tracker-details.html', last_days=last_days, username=username, tracker=tracker, logs=logs,
                           timestamps=timestamps, values=values)


@app.route("/tracker/<string:tracker_id>/log", methods=["GET", "POST"])
def tracker_logs(tracker_id):
    username = request.cookies.get('username')
    tracker = Tracker.query.filter_by(id=tracker_id).first()
    if request.method == 'GET':
        return render_template('log.html', username=username, tracker=tracker)
    elif request.method=='POST':
        timestamp=request.form['timestamp']
        value=request.form.getlist('value')
        notes=request.form['notes']
        s = Log(timestamp=timestamp, tracker=tracker_id, value=",".join(value), note=notes)
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('trackers_page'))


@app.route("/tracker/<int:tracker_id>/log/<int:log_id>/update", methods=["GET", "POST"])
def log_update(tracker_id, log_id):
    username = request.cookies.get('username')
    if request.method == 'GET':
        tracker = Tracker.query.filter_by(id=tracker_id).first()
        log = Log.query.filter_by(id=log_id).first()
        return render_template('log-update.html', username=username, tracker=tracker, log=log)
    elif request.method=='POST':
        timestamp = request.form['timestamp']
        value = request.form.getlist('value')
        notes = request.form['notes']
        s = Log.query.filter_by(id=log_id).update(dict(timestamp=timestamp, value=",".join(value), note=notes))
        db.session.commit()
        return redirect(url_for('tracker_details_page', tracker_id=tracker_id))


@app.route("/tracker/<int:tracker_id>/log/<int:log_id>/delete")
def log_delete(tracker_id,log_id):
    Log.query.filter_by(id=log_id).delete()
    db.session.commit()
    return redirect(url_for('tracker_details_page', tracker_id=tracker_id))


@app.route("/logout")
def logout():
    res = make_response(redirect(url_for('login')))
    res.delete_cookie('username')
    return res


class TrackerApi(Resource):

    @marshal_with(tracker_fields)
    def get(self, tracker_id):
        user = db.session.query(Tracker).filter(Tracker.id == tracker_id).first()
        if user:
            return user
        else:
            raise InputValidationError(404, 'Course not found')

    @marshal_with(tracker_fields)
    def put(self, tracker_id):
        args = create_tracking_parser.parse_args()
        name = args.get('name', None)
        description = args.get('description', None)
        # Sandeep - Validation required on type - boolean,duration,choice,numeric
        type = args.get('type', None)
        settings = args.get('settings', None)
        if name is None or name.isnumeric():
            raise BusinessValidationError(400, 'TRACER001', 'Tracker Name is required and should be string.')
        if description is None or description.isnumeric():
            raise BusinessValidationError(400, 'TRACKER002', 'Tracker Description is required and should be string.')
        if type is None or not (type=='boolean' or type == 'duration' or type == 'choice' or type == 'numeric'):
            raise BusinessValidationError(400, 'TRACKER003', 'Tracker Type is required and should be valid.')
        if settings.isnumeric():
            raise BusinessValidationError(400, 'TRACKER004', 'Tracker Settings Description should be string.')
        user_by_tracking_id = db.session.query(Tracker).filter(Tracker.id == tracker_id).first()
        if user_by_tracking_id is None:
            raise InputValidationError(404, 'Tracking not found')
        user_by_tracking_id.name = name
        user_by_tracking_id.description = description
        user_by_tracking_id.type = type
        user_by_tracking_id.settings = settings
        db.session.add(user_by_tracking_id)
        db.session.commit()
        return user_by_tracking_id, 200

    def delete(self, tracker_id):
        user = db.session.query(Tracker).filter(Tracker.id == tracker_id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            logs = db.session.query(Log).filter(Log.tracker == tracker_id).all()
            if logs:
                db.session.delete(logs)
                db.session.commit()
        else:
            raise InputValidationError(404, 'Tracker not found')
        return "Successfully Deleted", 200

    @marshal_with(tracker_fields)
    def post(self):
        args = create_tracking_parser.parse_args()
        name = args.get('name', None)
        description = args.get('description', None)
        type = args.get('type', None)
        settings = args.get('settings', None)
        if name is None or name.isnumeric():
            raise BusinessValidationError(400, 'TRACER001', 'Tracker Name is required and should be string.')
        if description is None or description.isnumeric():
            raise BusinessValidationError(400, 'TRACKER002', 'Tracker Description is required and should be string.')
        if type is None or not (type == 'boolean' or type == 'duration' or type == 'choice' or type == 'numeric'):
            raise BusinessValidationError(400, 'TRACKER003', 'Tracker Type is required and should be valid.')
        if settings.isnumeric():
            raise BusinessValidationError(400, 'TRACKER004', 'Tracker Settings Description should be string.')
        user_by_tracking_id = db.session.query(Tracker).filter(Tracker.name == name).first()
        if user_by_tracking_id:
            raise InputValidationError(409, 'Tracking Name already exist')
        new_tracker = Tracker(name=name, description=description, type=type, settings=settings)
        db.session.add(new_tracker)
        db.session.commit()
        return new_tracker, 201


class LogsApi(Resource):

    @marshal_with(log_fields)
    def get(self, tracker_id):
        last_days = int(request.args.get('lastdays', 30))
        filter_after = datetime.today() - timedelta(days=last_days)
        logs = db.session.query(Log).filter(Log.tracker == tracker_id).filter(Log.timestamp >= filter_after).order_by(
            Log.timestamp).all()
        return logs


class LogApi(Resource):

    @marshal_with(log_fields)
    def get(self, tracker_id, log_id):
        user = db.session.query(Log).filter(Log.id == log_id).first()
        if user:
            return user
        else:
            raise InputValidationError(404, 'Log not found')

    @marshal_with(log_fields)
    def put(self, tracker_id, log_id):
        args = create_log_parser.parse_args()
        timestamp = args.get('timestamp', None)
        tracker = args.get('tracker', None)
        value = args.get('value', None)
        note = args.get('note', None)
        user_by_log_id = db.session.query(Log).filter(Log.id == log_id).first()
        if user_by_log_id is None:
            raise InputValidationError(404, 'Log not found')
        if timestamp is None:
            raise BusinessValidationError(400, 'LOG002', 'Log timestamp is required')
        if tracker is None or not tracker.isnumeric():
            raise BusinessValidationError(400, 'LOG001', 'Log tracker id is required and should be String')
        if value is None or value.isnumeric():
            raise BusinessValidationError(400, 'LOG003', 'Log value is required and should be String')
        if note.isnumeric():
            raise BusinessValidationError(400, 'LOG004', 'Log note should be String')
        user_by_log_id.timestamp = timestamp
        user_by_log_id.tracker = tracker
        user_by_log_id.value = value
        user_by_log_id.note = note
        db.session.add(user_by_log_id)
        db.session.commit()
        return user_by_log_id, 200

    def delete(self, tracker_id, log_id):
        user = db.session.query(Log).filter(Log.id == log_id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
        else:
            raise InputValidationError(404, 'Log is not found')
        return "Successfully Deleted", 200

    @marshal_with(log_fields)
    def post(self, tracker_id):
        args = create_log_parser.parse_args()
        timestamp = args.get('timestamp', None)
        tracker = args.get('tracker', None)
        value = args.get('value', None)
        note = args.get('note', None)
        if timestamp is None:
            raise BusinessValidationError(400, 'LOG002', 'Log timestamp is required')
        if tracker is None or not tracker.isnumeric():
            raise BusinessValidationError(400, 'LOG001', 'Log tracker id is required and should be String')
        if value is None or value.isnumeric():
            raise BusinessValidationError(400, 'LOG003', 'Log value is required and should be String')
        if note.isnumeric():
            raise BusinessValidationError(400, 'LOG004', 'Log note should be String')
        new_log = Log(timestamp=timestamp, tracker=tracker, value=value, note=note)
        db.session.add(new_log)
        db.session.commit()
        return new_log, 201


api.add_resource(TrackerApi, '/api/tracker', '/api/tracker/<int:tracker_id>')
api.add_resource(LogApi, '/api/tracker/<int:tracker_id>/log', '/api/tracker/<int:tracker_id>/log/<int:log_id>')
api.add_resource(LogsApi, '/api/tracker/<int:tracker_id>/logs')


if __name__ == '__main__':
    app.run(debug=True)