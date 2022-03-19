from .database import db


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