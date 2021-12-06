from models.models import Task, db, File
from celery import Celery
from app import *
import os


celery = Celery('files', broker='redis://localhost:6379/0')

@celery.task(bind=True, name='process_files')
def process_files(args):
    with app.app_context():
        try:
            task = Task.query.filter(Task.status=='UPLOADED').first()
            file = File.query.filter(File.task==task.id).first()
            file_name_no_ext = file.name.split('.')[0]
            base_path = os.path.join(os.getcwd(), 'static/files')
            input_file = file.file_url
            output_file = os.path.join(base_path, file_name_no_ext+'.'+task.convert_to.lower())        
            script = "ffmpeg -y -i " + input_file+" "+output_file
            os.system(script)

            task.status = 'PROCESSED'

            db.session.commit()

            new_file = File(
                name = file_name_no_ext+'.'+task.convert_to.lower(),
                file_url = output_file,
                original = False,
                task = task.id
            )

            db.session.add(new_file)
            db.session.commit()

        except AttributeError:
            print('No data')

celery.conf.beat_schedule = {
    'Ejecutar cada 5s': {
        'task': 'process_files',
        'schedule': 5.0
    },
}