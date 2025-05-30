# core/utils.py
from django.utils import timezone
from .models import Message

def deliver_due_messages_for_user(user):
    now = timezone.now()
    due_messages = Message.objects.filter(
        recipient=user,
        scheduled_time__lte=now,
        delivered=False
    )
    count = 0
    for msg in due_messages:
        msg.delivered = True
        msg.delivered_at = now
        msg.save()
        count += 1
    return count
