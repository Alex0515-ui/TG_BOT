from celery import Celery

celery_app = Celery("bot", broker="redis://redis:6379/0", backend="redis://redis:6379/0", include=["tasks"])

celery_app.conf.update(
    task_serializer="json", 
    accept_content=["json"], 
    result_serializer="json", 
    timezone="UTC", enable_utc=True
)

celery_app.conf.beat_schedule = {
    'send-review-every-3-hours': {
        'task': 'tasks.Check_repetitions',
        'schedule': 10800
    }
}

