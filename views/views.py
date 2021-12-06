from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from models.models import User, File, Task, db, TaskSchema, FileSchema
from sqlalchemy.exc import IntegrityError 
from flask_restful import Resource
from flask import request
import datetime
import string
import os

task_schema = TaskSchema()
file_schema = FileSchema()

class HelloWorldView(Resource):
    def get(self):
        data = {
            "msj" : "Hello world"
        }
        return data, 200

class Tasks1View(Resource):
    def get(self):
        params = request.args
        max_task = int(params.get('max'))
        order_task = int(params.get('order'))
        if order_task == 0:
            tasks = Task.query.filter(Task.user==1).order_by(Task.id.asc())
        elif order_task == 1:
            tasks = Task.query.filter(Task.user==1).order_by(Task.id.desc())
        else:
            db.session.rollback()
            data = {
                    "error" : "Order value is not valid. 0 to ascendent order or 1 to descendent order"
                }
            return data, 400

        task_list = []
        for task in tasks:
            task_list.append(task)

        task_list = task_list[0:max_task]
        return [task_schema.dump(task) for task in task_list]
    
class Task1View(Resource):
    def get(self, task_id):
        return task_schema.dump(Task.query.get_or_404(task_id))

class UsersView(Resource):

    def post(self):
        data = request.json
        user = User(
            username = data['username'],
            email = data['email'],
            password = data['password1']
        )

        try:
            user.check_password(data['password1'], data['password2'])
            user.set_password(data['password1'])
            db.session.add(user)
            db.session.commit()
            data = {
                "message" : "Account created succesfully."
            }
            return data, 201
        except AssertionError as err:
            db.session.rollback()
            data = {
                "error" : err.args[0]
            }
            return data, 400
        except IntegrityError:
            db.session.rollback()
            data = {
                "error" : "the user already exists, please try with another user or email."
            }
            return data, 400

class LoginView(Resource):

    def post(self):
        user = User.query.filter(
            User.username == request.json["username"],
            User.password == request.json["password"]).first()
        if user is None:
            db.session.rollback()
            return "User does not exist", 404
        else:
            access_token = create_access_token(identity = user.id)
            return {"message":"Correct login", "token": access_token}, 200

class TasksView(Resource):
    @jwt_required()
    def post(self):
        file = request.files['fileName']
        if file:
            if not self.contains_whitespace(file.filename):
                db.session.rollback()
                base_path = os.path.join(os.getcwd(), 'static/files')
                file_path = os.path.join(base_path, file.filename)
                file.save(file_path)
                new_file = File(
                    name = file.filename,
                    file_url = file_path,
                    original = True
                )

                new_task = Task(
                    timeStamp = datetime.datetime.now(),
                    status = "UPLOADED",
                    file = new_file,
                    user = get_jwt_identity(),
                    convert_to = request.form['newFormat']
                )

                db.session.add(new_file)
                db.session.add(new_task)
                new_file.task = new_task
                db.session.commit()

                data = {
                    "message" : "Task created sucessfully."
                }

                return data, 200

            else:
                db.session.rollback()
                data = {
                    "error" : "File name can not contain white spaces in the name"
                }
                return data, 400
        else:
            db.session.rollback()
            data = {
                    "error" : "fileName is required"
                }
            return data, 400


    def contains_whitespace(self, s):
        return True in [c in s for c in string.whitespace]

    @jwt_required()
    def get(self):
        params = request.args
        max_task = int(params.get('max'))
        order_task = int(params.get('order'))
        if order_task == 0:
            tasks = Task.query.filter(Task.user==1).order_by(Task.id.asc())
        elif order_task == 1:
            tasks = Task.query.filter(Task.user==1).order_by(Task.id.desc())
        else:
            db.session.rollback()
            data = {
                    "error" : "Order value is not valid. 0 to ascendent order or 1 to descendent order"
                }
            return data, 400

        task_list = []
        for task in tasks:
            task_list.append(task)

        task_list = task_list[0:max_task]
        return [task_schema.dump(task) for task in task_list]

class TaskView(Resource):
    @jwt_required()
    def get(self, task_id):
        return task_schema.dump(Task.query.get_or_404(task_id))

    @jwt_required()
    def put(self, task_id):
        data = request.json
        task = Task.query.get_or_404(task_id)
        file = File.query.filter(File.task==task.id, File.original==False).first()
        if task.status.name == 'PROCESSED':
            db.session.delete(file)
            db.session.commit()

            task.status = 'UPLOADED'

        task.convert_to = data['newFormat']
        db.session.commit()

        return task_schema.dump(task), 200

    @jwt_required()
    def delete(self, task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return '',204

class FilesView(Resource):
    @jwt_required()
    def get(self, file_name):
        file = File.query.filter(File.name==file_name).first()
        if file:
            return file_schema.dump(file)
        else:
            
            data = {
                    "error" : "File is not found"
                }
            return data, 404