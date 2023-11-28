import time

from celery import shared_task
from celery_singleton import Singleton
from django.db.models import F


@shared_task(base=Singleton)
def set_price(subscriptions_ids):
    from services.models import Subscription
    subscriptions = Subscription.objects.filter(id__in=subscriptions_ids).only('id').annotate(
        annotated_price=F('service__full_price') * (1 - (F('plan__discount_percent') / 100.00)))
    for s in subscriptions:
        s.price = s.annotated_price
    Subscription.objects.bulk_update(subscriptions, ["price"])
