from celery import Celery


app = Celery(
    'netphazz',
    include=['netphazz.tasks']
)
app.config_from_object('netphazz.config')
