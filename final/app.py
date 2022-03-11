from flask import Flask, render_template, request, redirect, url_for, make_response
import os

from flask_sqlalchemy import SQLAlchemy

app = None
db = SQLAlchemy()


def create_app():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, 'tracker-db.db')
    db.init_app(app)
    app.app_context().push()
    return app


app = create_app()

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
    timestamp = db.Column(db.String, primary_key=True)
    tracker = db.Column(db.Integer, db.ForeignKey('tracker.id'), nullable=False)
    value = db.Column(db.String, nullable=False)
    note = db.Column(db.String)


@app.route("/", methods=["GET", "POST"])
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
    trackers = Tracker.query.all()
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


@app.route("/tracker/<string:tracker_id>")
def tracker_details_page(tracker_id):
    username = request.cookies.get('username')
    tracker = Tracker.query.filter_by(id=tracker_id).first()
    logs = Log.query.filter_by(tracker=tracker_id).all()
    return render_template('tracker-details.html', username=username, tracker=tracker, logs=logs)


@app.route("/tracker/<string:tracker_id>/log", methods=["GET", "POST"])
def tracker_logs(tracker_id):
    username = request.cookies.get('username')
    tracker = Tracker.query.filter_by(id=tracker_id).first()
    if request.method == 'GET':
        return render_template('log.html', username=username, tracker=tracker)
    elif request.method=='POST':
        timestamp=request.form['timestamp']
        value=request.form['value']
        notes=request.form['notes']
        s = Log(timestamp=timestamp, tracker=tracker_id, value=value, note=notes)
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('trackers_page'))


@app.route("/logout")
def logout():
    res = make_response(redirect(url_for('login')))
    res.delete_cookie('username')
    return res


# @app.route("/student/create", methods=["GET", "POST"])
# def create():
#     if request.form:
#         roll=request.form['roll']
#         fname=request.form['f_name']
#         lname=request.form['l_name']
#         missing=Student.query.filter_by(roll_number=roll).first()
#         if missing is None:
#             s=Student(roll_number=roll,first_name=fname,last_name=lname)
#             db.session.add(s)
#             db.session.commit()
#             return redirect(url_for('home'))
#         else:
#             return render_template('user-exists.html')
#     return render_template('create.html')
#
#
# @app.route("/student/<int:student_id>/update", methods=["GET", "POST"])
# def update(student_id):
#     if request.method == 'GET':
#         this_student = Student.query.filter_by(student_id=student_id).first()
#         courses = Course.query.all()
#         return render_template('log.html', student=this_student, courses=courses)
#
#     elif request.method=='POST':
#         fname=request.form['f_name']
#         lname=request.form['l_name']
#         course=request.form['course']
#         s=Student.query.filter_by(student_id=student_id).update(dict(first_name=fname,last_name=lname))
#         db.session.commit()
#         this_course = Course.query.filter_by(course_id=course).first()
#         cid = this_course.course_id
#         s = Enrollments(estudent_id=student_id, ecourse_id=cid)
#         db.session.add(s)
#         db.session.commit()
#         return redirect(url_for('home'))
#
#
# @app.route("/student/<int:student_id>")
# def student(student_id):
#     student = Student.query.filter_by(student_id=student_id).first()
#     enrolls = Enrollments.query.with_entities(Enrollments.ecourse_id).filter_by(estudent_id=student_id).all()
#     cid = []
#     for enroll in enrolls:
#         cid.append(enroll[0])
#     courses = Course.query.filter(Course.course_id.in_(cid)).all()
#     return render_template('tracker-details.html', student=student, courses=courses)
#
#
# @app.route('/student/<int:student_id>/delete')
# def delete(student_id):
#     Student.query.filter_by(student_id=student_id).delete()
#     Enrollments.query.filter_by(estudent_id=student_id).delete()
#     db.session.commit()
#     return redirect(url_for('home'))
#
#
# @app.route('/student/<int:student_id>/withdraw/<int:course_id>')
# def withdraw(student_id, course_id):
#     Enrollments.query.filter_by(estudent_id=student_id).filter_by(ecourse_id=course_id).delete()
#     db.session.commit()
#     return redirect(url_for('home'))
#
#
# @app.route("/courses")
# def courses():
#     courses = Course.query.all()
#     return render_template('login.html', courses=courses)
#
#
# @app.route("/course/<int:course_id>", methods=["GET", "POST"])
# def course(course_id):
#     course = Course.query.filter_by(course_id=course_id).first()
#     enrolls = Enrollments.query.with_entities(Enrollments.estudent_id).filter_by(ecourse_id=course_id).all()
#     cid = []
#     for enroll in enrolls:
#         cid.append(enroll[0])
#     # print(cid)
#     students = Student.query.filter(Student.student_id.in_(cid)).all()
#     #print(student)
#     return render_template('trackers.html', course=course, students=students)
#
#
# @app.route("/course/create", methods=["GET", "POST"])
# def course_create():
#     if request.form:
#         course_description=request.form['desc']
#         course_code=request.form['code']
#         course_name=request.form['c_name']
#         missing=Course.query.filter_by(course_code=course_code).first()
#         if missing is None:
#             s=Course(course_code=course_code,course_name=course_name,course_description=course_description)
#             db.session.add(s)
#             db.session.commit()
#             return redirect(url_for('courses'))
#         else:
#             return render_template('course-exists.html')
#     return render_template('tracker-create.html')
#
#
# @app.route("/course/<int:course_id>/update", methods=["GET", "POST"])
# def course_update(course_id):
#     if request.method == 'GET':
#         this_course = Course.query.filter_by(course_id=course_id).first()
#         return render_template('course_update.html', course=this_course)
#
#     elif request.method=='POST':
#         c_name=request.form['c_name']
#         desc=request.form['desc']
#         s=Course.query.filter_by(course_id=course_id).update(dict(course_name=c_name,course_description=desc))
#         db.session.commit()
#         return redirect(url_for('courses'))
#
#
# @app.route('/course/<int:course_id>/delete')
# def course_delete(course_id):
#     Course.query.filter_by(course_id=course_id).delete()
#     Enrollments.query.filter_by(ecourse_id=course_id).delete()
#     db.session.commit()
#     return redirect(url_for('courses'))


if __name__ == '__main__':
    app.run(debug=True)