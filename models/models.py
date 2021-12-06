from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
import enum
import  re

db = SQLAlchemy()

class Status(enum.Enum):
    UPLOADED = 1
    PROCESSED = 2

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(128), unique = True)
    email = db.Column(db.String(128), unique = True)
    password = db.Column(db.String(80))
    tasks = db.relationship("Task", backref="users", lazy='dynamic')

    def check_password(self, password1, password2):
        if password1 != password2:
            raise AssertionError('Passwords does not match.')
        return password1

    def set_password(self, password):
        if not password:
            raise AssertionError('Password not provided')
        if not re.match('\d.*[A-Z]|[A-Z].*\d', password):
            raise AssertionError('Password must contain 1 capital letter and 1 number')
        if len(password) < 8:
            raise AssertionError('Password must be at least 8 characters')
        self.password = password

class File(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(128), unique = True)
    file_url = db.Column(db.String(250), unique = True)
    original = db.Column(db.Boolean)
    task = db.Column(db.Integer, db.ForeignKey('task.id'))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    timeStamp = db.Column(db.DateTime())
    status = db.Column((db.Enum(Status)))
    user = db.Column(db.Integer, db.ForeignKey('user.id'))
    convert_to = db.Column(db.String(128))
    file = db.relationship('File', backref='tasks', uselist=False)

class EnumToDict(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return {"key": value.name, "value": value.value}

class TaskSchema(SQLAlchemyAutoSchema):
    status = EnumToDict(attribute=("status"))
    class Meta:
         model = Task
         include_relationships = True
         load_instance = True 

class FileSchema(SQLAlchemyAutoSchema):
    class Meta:
         model = File
         include_relationships = True
         load_instance = True 