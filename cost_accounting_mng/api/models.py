import json
from django.db import models
from django.contrib.auth.models import User


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


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='balance')
    balance = models.DecimalField(max_digits=11, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user}, ({self.balance})"


class Category(models.Model):
    creator_choices = [
        ('D', 'Default'),
        ('U', 'User'),]

    title = models.CharField(max_length=150, unique=True, null=False)
    inf = models.CharField(max_length=1, choices=creator_choices, default='U')
    users = models.ManyToManyField(User, related_name='categories')

    def __str__(self):
        return f'{self.title}: {self.inf}'



class Operations(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operations')
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    rest_balance = models.DecimalField(max_digits=11, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    organization = models.CharField(max_length=40, blank=False)
    description = models.TextField(blank=True, null=True)
    #
    # class Meta:
    #     get_latest_by = ["date"]

    def __str__(self):
        return f'{self.user}: {self.amount:+}'
