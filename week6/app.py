from flask import Flask, make_response
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

student_fields = {
    'student_id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'roll_number': fields.String
}

create_course_parser = reqparse.RequestParser()
create_course_parser.add_argument('course_name')
create_course_parser.add_argument('course_code')
create_course_parser.add_argument('course_description')

create_student_parser = reqparse.RequestParser()
create_student_parser.add_argument('first_name')
create_student_parser.add_argument('last_name')
create_student_parser.add_argument('roll_number')


class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        error_json = {"error_code": error_code, 'error_message': error_message}
        self.response = make_response(json.dumps(error_json), status_code)


class InputValidationError(HTTPException):
    def __init__(self, status_code, error_message):
        self.response = make_response(error_message, status_code)


# String validation yet to be done
class CourseApi(Resource):

    @marshal_with(course_fields)
    def get(self, course_id):
        user = db.session.query(Course).filter(Course.course_id == course_id).first()
        # print(user)
        if user:
            return user
        else:
            raise InputValidationError(404, 'Course not found')

    @marshal_with(course_fields)
    def put(self, course_id):
        args = create_course_parser.parse_args()
        course_name = args.get('course_name', None)
        course_code = args.get('course_code', None)
        course_description = args.get('course_description', None)
        if course_name is None:
            raise BusinessValidationError(400, 'COURSE001', 'Course Name is required and should be string.')
        if course_code is None:
            raise BusinessValidationError(400, 'COURSE002', 'Course Code is required and should be string.')
        print(not isinstance(course_description, str))
        if not isinstance(course_description, str):
            raise BusinessValidationError(400, 'COURSE003', 'Course Description should be string.')
        user_by_course_id = db.session.query(Course).filter(Course.course_id == course_id).first()
        if user_by_course_id is None:
            raise InputValidationError(404, 'Course not found')
        user_by_course_id.course_name = course_name
        user_by_course_id.course_code = course_code
        user_by_course_id.course_description = course_description
        db.session.add(user_by_course_id)
        db.session.commit()
        return user_by_course_id, 200

    def delete(self, course_id):
        user = db.session.query(Course).filter(Course.course_id == course_id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
        else:
            raise InputValidationError(404, 'Course not found')
        return "Successfully Deleted", 200

    @marshal_with(course_fields)
    def post(self):
        args = create_course_parser.parse_args()
        course_name = args.get('course_name')
        course_code = args.get('course_code')
        course_description = args.get('course_description')
        if course_name is None:
            raise BusinessValidationError(400, 'COURSE001', 'Course Name is required and should be string.')
        if course_code is None:
            raise BusinessValidationError(400, 'COURSE002', 'Course Code is required and should be string.')
        # print(type(course_description))
        if not isinstance(course_description, str):
            raise BusinessValidationError(400, 'COURSE003', 'Course Description should be string.')
        user = db.session.query(Course).filter(Course.course_code == course_code).first()
        if user:
            raise InputValidationError(409, 'course_code already exist')
        new_course = Course(course_name=course_name, course_code=course_code, course_description=course_description)
        db.session.add(new_course)
        db.session.commit()
        return new_course, 201


# String validation yet to be done
class StudentApi(Resource):

    @marshal_with(student_fields)
    def get(self, student_id):
        user = db.session.query(Student).filter(Student.student_id == student_id).first()
        # print(user)
        if user:
            return user
        else:
            raise InputValidationError(404, 'Student not found')

    @marshal_with(student_fields)
    def put(self, student_id):
        args = create_student_parser.parse_args()
        first_name = args.get('first_name', None)
        last_name = args.get('last_name', None)
        roll_number = args.get('roll_number', None)
        if first_name is None:
            raise BusinessValidationError(400, 'STUDENT002', 'First Name is required and should be String')
        if roll_number is None:
            raise BusinessValidationError(400, 'STUDENT001', 'Roll Number required and should be String')
        print(not isinstance(last_name, str))
        if not isinstance(last_name, str):
            raise BusinessValidationError(400, 'STUDENT003', 'Last Name is String')
        user_by_student_id = db.session.query(Student).filter(Student.student_id == student_id).first()
        if user_by_student_id is None:
            raise InputValidationError(404, 'Student not found')
        user_by_student_id.roll_number = roll_number
        user_by_student_id.first_name = first_name
        user_by_student_id.last_name = last_name
        db.session.add(user_by_student_id)
        db.session.commit()
        return user_by_student_id, 200

    def delete(self, student_id):
        user = db.session.query(Student).filter(Student.student_id == student_id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
        else:
            raise InputValidationError(404, 'Student not found')
        return "Successfully Deleted", 200

    @marshal_with(student_fields)
    def post(self):
        args = create_student_parser.parse_args()
        first_name = args.get('first_name', None)
        last_name = args.get('last_name', None)
        roll_number = args.get('roll_number', None)
        if first_name is None:
            raise BusinessValidationError(400, 'STUDENT002', 'First Name is required and should be String')
        if roll_number is None:
            raise BusinessValidationError(400, 'STUDENT001', 'Roll Number required and should be String')
        print(not isinstance(last_name, str))
        if not isinstance(last_name, str):
            raise BusinessValidationError(400, 'STUDENT003', 'Last Name is String')
        user = db.session.query(Student).filter(Student.roll_number == roll_number).first()
        if user:
            raise InputValidationError(409, 'Student already exist')
        new_student = Student(roll_number=roll_number, first_name=first_name, last_name=last_name)
        db.session.add(new_student)
        db.session.commit()
        return new_student, 201


api.add_resource(CourseApi, '/api/course', '/api/course/<int:course_id>')
api.add_resource(StudentApi, '/api/student', '/api/student/<int:student_id>')

if __name__ == '__main__':
    app.run(debug=True)
