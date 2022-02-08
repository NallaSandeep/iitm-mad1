from flask import Flask, render_template,request,redirect,url_for
import os

from flask_sqlalchemy import SQLAlchemy

app = None
db = SQLAlchemy()


def create_app():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, 'database.sqlite3')
    db.init_app(app)
    app.app_context().push()
    return app


app = create_app()


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


@app.route("/", methods=["GET", "POST"])
def home():
    students = Student.query.all()
    #print(students)
    return render_template('studentsList.html', students=students)


@app.route("/student/create", methods=["GET", "POST"])
def create():
    if request.form:
        roll=request.form['roll']
        fname=request.form['f_name']
        lname=request.form['l_name']
        courses=request.form.getlist('courses')

        missing=Student.query.filter_by(roll_number=roll).first()
        if missing is None:
            # If roll number not exists
            s=Student(roll_number=roll,first_name=fname,last_name=lname)
            db.session.add(s)
            db.session.commit()

            this_student=Student.query.filter_by(roll_number=roll).first()
            s_id=this_student.student_id
            for course in courses:
                print(course)
                missing = Student.query.filter_by(roll_number=roll).first()
                if course=='course_1':
                    cid=1
                elif course=='course_2':
                    cid=2
                elif course=='course_3':
                    cid=3
                elif course=='course_4':
                    cid=4
                c=Enrollments(estudent_id=s_id,ecourse_id=cid)
                db.session.add(c)
                db.session.commit()
            return redirect(url_for('home'))
        else:
            return render_template('user-exists.html')
    return render_template('create.html')


@app.route("/student/<int:student_id>/update", methods=["GET", "POST"])
def update(student_id):
    if request.method == 'GET':
        this_student = Student.query.filter_by(student_id=student_id).first()

        enrolls_cid = Enrollments.query.with_entities(Enrollments.ecourse_id).filter_by(estudent_id=student_id).all()
        cid = []
        for enroll in enrolls_cid:
            cid.append(enroll[0])
        # print(cid)
        return render_template('update.html', student=this_student, cid=cid)

    elif request.method=='POST':
        fname=request.form['f_name']
        lname=request.form['l_name']
        courses=request.form.getlist('courses')
        s=Student.query.filter_by(student_id=student_id).update(dict(first_name=fname,last_name=lname))
        db.session.commit()

        Enrollments.query.filter_by(estudent_id=student_id).delete()
        db.session.commit()
        for course in courses:
            if course=='course_1':
                cid=1
            elif course=='course_2':
                cid=2
            elif course=='course_3':
                cid=3
            elif course=='course_4':
                cid=4
            c=Enrollments(estudent_id=student_id,ecourse_id=cid)
            db.session.add(c)
            db.session.commit()
        return redirect(url_for('home'))


@app.route("/student/<int:student_id>", methods=["GET", "POST"])
def student(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    enrolls = Enrollments.query.with_entities(Enrollments.ecourse_id).filter_by(estudent_id=student_id).all()
    cid = []
    for enroll in enrolls:
        cid.append(enroll[0])
    # print(cid)
    courses = Course.query.filter(Course.course_id.in_(cid)).all()
    #print(student)
    return render_template('student.html', student=student, courses=courses)

@app.route('/student/<int:student_id>/delete')
def delete(student_id):
    Student.query.filter_by(student_id=student_id).delete()
    Enrollments.query.filter_by(estudent_id=student_id).delete()
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
