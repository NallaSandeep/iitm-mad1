import flask
from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import datetime, timedelta

from flask_login import login_required
from flask_security import roles_required, LoginForm, login_user
from sqlalchemy.sql.functions import user

from .models import User, Log, Tracker
from .database import db
from flask import current_app as app


@app.route("/")
def home():
    return render_template('home.html')


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.form:
#         username=request.form['user-name']
#         password=request.form['password']
#         missing=User.query.filter_by(username=username).first()
#         if missing is None:
#             return redirect(url_for('login'))
#         else:
#             resp = make_response(redirect(url_for('trackers_page')))
#             resp.set_cookie('username', username)
#             return resp
#     return render_template('login.html')


@app.route("/trackers")
@login_required
def trackers_page():
    username = request.cookies.get('username')
    latest_logs = db.session.query(
        Log.tracker, db.func.max(Log.timestamp).label('last_tracked')
    ).group_by(Log.tracker).subquery()
    trackers = db.session.query(Tracker.id, Tracker.name, latest_logs.c.last_tracked).outerjoin(latest_logs, Tracker.id ==
                                                                               latest_logs.c.tracker)
    return render_template('trackers-get.html', username=username, trackers=trackers)


@app.route("/trackers/<string:tracker_id>")
@login_required
def tracker_page(tracker_id):
    username = request.cookies.get('username')
    tracker = Tracker.query.filter_by(id=tracker_id).first()
    return render_template('tracker-get.html', username=username, tracker=tracker)


@app.route("/trackers/create", methods=["GET", "POST"])
@login_required
@roles_required('admin')
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


@app.route("/trackers/<string:tracker_id>/update", methods=["GET", "POST"])
@login_required
@roles_required('admin')
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


@app.route("/trackers/<string:tracker_id>/delete")
@login_required
@roles_required('admin')
def trackers_delete(tracker_id):
    Tracker.query.filter_by(id=tracker_id).delete()
    Log.query.filter_by(tracker=tracker_id).delete()
    db.session.commit()
    return redirect(url_for('trackers_page'))


@app.route("/trackers/<string:tracker_id>/logs")
@login_required
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
    return render_template('logs-get.html', last_days=last_days, username=username, tracker=tracker, logs=logs,
                           timestamps=timestamps, values=values)


@app.route("/trackers/<string:tracker_id>/logs/<int:log_id>", methods=["GET", "POST"])
@login_required
def tracker_log(tracker_id, log_id):
    username = request.cookies.get('username')
    tracker = Tracker.query.filter_by(id=tracker_id).first()
    log = Log.query.filter_by(id=log_id).first()
    return render_template('log-get.html', username=username, tracker=tracker, log=log)


@app.route("/trackers/<string:tracker_id>/logs/create", methods=["GET", "POST"])
@login_required
def tracker_logs(tracker_id):
    username = request.cookies.get('username')
    tracker = Tracker.query.filter_by(id=tracker_id).first()
    if request.method == 'GET':
        return render_template('log-create.html', username=username, tracker=tracker)
    elif request.method=='POST':
        timestamp=request.form['timestamp']
        value=request.form.getlist('value')
        notes=request.form['notes']
        s = Log(timestamp=timestamp, tracker=tracker_id, value=",".join(value), note=notes)
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('trackers_page'))


@app.route("/trackers/<int:tracker_id>/logs/<int:log_id>/update", methods=["GET", "POST"])
@login_required
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


@app.route("/trackers/<int:tracker_id>/logs/<int:log_id>/delete")
@login_required
def log_delete(tracker_id,log_id):
    Log.query.filter_by(id=log_id).delete()
    db.session.commit()
    return redirect(url_for('tracker_details_page', tracker_id=tracker_id))


@app.route("/not-found")
def not_found_page():
    return render_template("notfound.html"), 404


@app.route("/unauth")
def unauth_page():
    return render_template("unauth.html"), 403
