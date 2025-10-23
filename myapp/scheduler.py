from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from .models import User

def cleanup_task():
    old_users = User.objects.filter(role='viewer', Batch = 1)
    count = old_users.count()
    old_users.delete()
    print(f"[APScheduler] Deleted {count} old users at {timezone.now()}")

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(cleanup_task, 'interval', hours=24)
    scheduler.start()
