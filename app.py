from views.views import UsersView, LoginView, TasksView, FilesView, Tasks1View, Task1View, HelloWorldView
from views.views import TaskView
from flask_jwt_extended import JWTManager
from flask_restful import Api
from models.models import db
from flask import Flask
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app_context = app.app_context()
app_context.push()

if app.config['ENV'] == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

if __name__ == '__main__':
    app.run()
    
db.init_app(app)
db.create_all()

jwt = JWTManager(app)

api = Api(app)
api.add_resource(UsersView, '/api/auth/signup')
api.add_resource(LoginView, '/api/auth/login')
api.add_resource(TasksView, '/api/tasks')
api.add_resource(HelloWorldView, '/api/hello')
api.add_resource(Tasks1View, '/api/tasks1')
api.add_resource(Task1View, '/api/tasks1/<int:task_id>')
api.add_resource(TaskView, '/api/tasks/<int:task_id>')
api.add_resource(FilesView, '/api/files/<string:file_name>')