from django.core.validators import MaxValueValidator
from django.db import models

from clients.models import Client
from services.tasks import set_price


class Service(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__full_price = self.full_price

    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        if self.full_price != self.__full_price:
            subscriptions_ids = [s.id for s in self.subscriptions.all()]
            set_price.delay(subscriptions_ids)
        return super().save(*args, **kwargs)


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount_percent = self.discount_percent

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    discount_percent = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])

    def save(self, *args, **kwargs):
        if self.discount_percent != self.__discount_percent:
            subscriptions_ids = [s.id for s in self.subscriptions.all()]
            set_price.delay(subscriptions_ids)
        return super().save(*args, **kwargs)


class Subscription(models.Model):
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)
