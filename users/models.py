from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        null=True,
        blank=True
    )
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.username
