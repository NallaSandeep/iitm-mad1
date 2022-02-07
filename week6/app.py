
from flask import Flask, render_template, request, redirect, url_for, make_response
import os

from flask_restful import Api, Resource, fields, marshal_with, reqparse
from flask_restful.representations import json
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException

app = None
api = None
db = SQLAlchemy()


def create_app():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, 'api_database.sqlite3')
    db.init_app(app)
    api = Api(app)
    app.app_context().push()
    return app, api


app, api = create_app()


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)


class Enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)


course_fields = {
    'course_id': fields.Integer,
    'course_name': fields.String,
    'course_code': fields.String,
    'course_description': fields.String
}


create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('course_name')
create_user_parser.add_argument('course_code')
create_user_parser.add_argument('course_description')


class NotFoundError(HTTPException):
    def __init__(self, error_code):
        self.response = make_response('', error_code)


class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        error_json = {"error_code": error_code,'error_message': error_message}
        self.response = make_response(json.dumps(error_json), status_code)

    def __init__(self, status_code, error_message):
        #error_json = {"error_code": error_code,'error_message': error_message}
        self.response = make_response(error_message, status_code)


class CourseApi(Resource):

    @marshal_with(course_fields)
    def get(self, course_id):
        user = db.session.query(Course).filter(Course.course_id == course_id).first()
        #print(user)
        if user:
            return user
        else:
            raise NotFoundError(error_code=404)

    def put(self, course_id):
        print("UPDATE", course_id)
        pass

    def delete(self, course_id):
        print("DELETE", course_id)
        pass

    @marshal_with(course_fields)
    def post(self):
        args = create_user_parser.parse_args()
        course_name = args.get('course_name', None)
        course_code = args.get('course_code', None)
        course_description = args.get('course_description', None)
        if course_name is None:
            raise BusinessValidationError(400, 'COURSE001', 'Course Name is required and should be string.')
        if course_code is None:
            raise BusinessValidationError(400, 'COURSE002', 'Course Code is required and should be string.')
        #print(type(course_description))
        if not isinstance(course_description, str):
            raise BusinessValidationError(400, 'COURSE003', 'Course Description should be string.')
        user = db.session.query(Course).filter(Course.course_code == course_code).first()
        if user:
            raise BusinessValidationError(409, 'course_code already exist')
        new_course = Course(course_name=course_name, course_code=course_code, course_description=course_description)
        db.session.add(new_course)
        db.session.commit()
        return new_course, 201


api.add_resource(CourseApi, '/api/course', '/api/course/<int:course_id>')

if __name__ == '__main__':
    app.run(debug=True)
