class Config(object):
    DEBUG = False
    TESTING = False
    JWT_SECRET_KEY = 'secret-key'
    UPLOAD_FOLDER = 'static/files'
    CELERY_RESULT_BACKEND = ''
    

class ProductionConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@prod.cvnfbhghkbwy.us-east-1.rds.amazonaws.com:5432/prod'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'