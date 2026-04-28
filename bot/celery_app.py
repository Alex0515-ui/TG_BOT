from celery import Celery
from datetime import timedelta

celery_app = Celery("bot", broker="redis://redis:6379/0", backend="redis://redis:6379/0", include=["tasks"])

# Настраиваем Celery
celery_app.conf.update(
    task_serializer="json", 
    accept_content=["json"], 
    result_serializer="json", 
    timezone="UTC", enable_utc=True
)

# Ставим время повторения
celery_app.conf.beat_schedule = {
    'send-review-every-6-hours': {
        'task': 'tasks.Check_repetitions',
        'schedule': timedelta(hours=12)
    }
}

