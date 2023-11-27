from celery import shared_task


@shared_task
def set_price(subscription_id):
    from services.models import Subscription
    subscription = Subscription.objects.filter(id=subscription_id).first()
    new_price = subscription.service.full_price * (1 - subscription.plan.discount_percent / 100)
    subscription.price = new_price
    subscription.save(update_fields=['price'])
