import json

from django.db import models
from django.contrib.auth.models import User, AbstractUser

# Create your models here.


default_categories = [
    "Забота о себе",
    "Зарплата",
    "Здоровье и фитнес",
    "Кафе и рестораны",
    "Машина",
    "Образование",
    "Отдых и развлечения",
    "Платежи, комиссии",
    "Покупки: одежда, техника",
    "Продукты",
    "Проезд",
]


def default_categories_json():
    return json.dumps(default_categories)


class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='balance')
    balance = models.DecimalField(max_digits=11, decimal_places=2)
    categories = models.TextField(blank=False, null=False, default=default_categories_json)

    def __str__(self):
        return f"{self.user}, ({self.balance})"


class Operations(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operations')
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    rest_balance = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, blank=False)
    organization = models.CharField(max_length=40, blank=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user}: {self.amount:+}'
