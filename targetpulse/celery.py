import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'targetpulse.settings')

app = Celery('targetpulse')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks() 