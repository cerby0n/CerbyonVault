import os 
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cerbyonvault.settings')

# Create a new Celery application instance with the project name.
app = Celery('cerbyonvault')

# Load Celery configuration from Django settings, using the 'CELERY_' namespace.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover asynchronous tasks from all registered Django app configs.
app.autodiscover_tasks()