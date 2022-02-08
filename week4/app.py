from flask import Flask
from flask import render_template
from flask import request
import csv
import matplotlib.pyplot as plt

app = Flask(__name__)


def render_wrong_html():
    return render_template("wrong.html")


def student_information(student_id, rows):
    value = 0
    for row in rows:
        if row[0] == student_id:
            value += int(row[2])
    if value == 0:
        student_template = render_wrong_html()
    else:
        student_template = render_template("student.html", student_id=student_id, student_list=rows, total=value)
    return student_template


def course_information(course_id, rows):
    value = 0
    max_score = 0
    count = 0
    data = {}
    for row in rows:
        try:
            course = int(course_id)
        except:
            break
        if int(row[1]) == course:
            i = int(row[2])
            value += i
            count += 1
            if i not in data.keys():
                data[i] = 1
            else:
                data[i] += 1
            if i > max_score:
                max_score = i
    if value == 0 or count == 0:
        student_template = render_wrong_html()
    else:
        avg = value / count
        courses = list(data.keys())
        values = list(data.values())
        fig = plt.figure(figsize=(10, 5))
        plt.bar(courses, values)
        plt.xlabel("Marks")
        plt.ylabel("Frequency")
        fig.savefig('./static/my_plot.png')
        student_template = render_template("course.html", course_id=course_id, average=avg, maximum=max_score)
    return student_template


@app.route("/", methods=['GET', 'POST'])
def student_course_information():
    if request.method == 'GET':
        return render_template("index.html")
    elif request.method == 'POST':
        fr = open('data.csv', 'r')
        csv_reader = csv.reader(fr)
        header = next(csv_reader)
        rows = []
        for row in csv_reader:
            rows.append(row)
        id_element = request.form.get("ID")
        id_value = request.form.get('id_value')
        if id_element == 'student_id':
            return student_information(id_value, rows)
        else:
            return course_information(id_value, rows)
    else:
        return render_wrong_html()


if __name__ == '__main__':
    app.run()
