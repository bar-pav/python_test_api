from django.db import models
from django.contrib.auth.models import User, AbstractUser

# Create your models here.


class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='balance')
    balance = models.DecimalField(max_digits=11, decimal_places=2)

    def __str__(self):
        return str(self.balance)


class Operations(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, blank=False)
    organization = models.CharField(max_length=40, blank=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.id}, {self.amount}'
