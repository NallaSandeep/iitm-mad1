from datetime import timedelta, datetime

from flask import request
from flask_restful import Api, Resource, fields, marshal_with, reqparse
from .models import User, Log, Tracker
from .database import db
from .validation import *

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
        if type is None or not (type == 'boolean' or type == 'duration' or type == 'choice' or type == 'numeric'):
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
            db.session.query(Log).filter(Log.tracker == tracker_id).delete()
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
