from django.db import models
from django.contrib.auth.models import User


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.SET_NULL, null=True)


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
