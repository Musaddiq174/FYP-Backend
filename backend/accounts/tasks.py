from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import ClassSessionData

@shared_task
def delete_expired_sessions():
    threshold_time = timezone.now() - timedelta(minutes=5)
    expired_sessions = ClassSessionData.objects.filter(scheduled_at__lt=threshold_time)
    count = expired_sessions.count()
    expired_sessions.delete()
    return f"Deleted {count} expired class sessions."
