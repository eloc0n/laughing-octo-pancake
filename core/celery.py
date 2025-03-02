import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_transport_options = {
    "visibility_timeout": settings.CELERY_VISIBILITY_TIMEOUT
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "task_to_pull_data_from_monitoring_service": {
        "task": "applications.plants.tasks.fetch_monitoring_data",
        # Execute everyday at 1am.
        "schedule": crontab(hour=1, minute=0),
        # For testing purpose. Execute every 2 minutes.
        # "schedule": crontab(minute="*/2"),
    },
}
