from datetime import date
from django.contrib.auth.models import User
from django.db import models


VACATION_DAYS_PER_YEAR = 15


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey("Team", on_delete=models.SET_NULL, null=True)
    vacation_days_taken = models.IntegerField(default=0)  # Days already taken
    start_date = models.DateField(default=date.today)  # Employee's start date

    def calculate_available_vacation_days(self):
        # Get today's date
        today = date.today()

        # Calculate full years worked
        years_worked = today.year - self.start_date.year

        # Adjust for anniversary date not yet reached this year
        if today < self.start_date.replace(year=today.year):
            years_worked -= 1

        # Handle prorated vacation days in the first year
        if years_worked == 0:
            days_since_start = (today - self.start_date).days
            days_in_year = 365
            prorated_vacation_days = (
                VACATION_DAYS_PER_YEAR / days_in_year
            ) * days_since_start
            total_vacation_days_accrued = prorated_vacation_days
        else:
            # Calculate total accrued vacation days for full years worked
            total_vacation_days_accrued = VACATION_DAYS_PER_YEAR * years_worked

        # Subtract vacation days already taken
        available_vacation_days = total_vacation_days_accrued - self.vacation_days_taken

        # Ensure no negative values are returned
        return max(available_vacation_days, 0)

    def __str__(self):
        return self.user.username


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Holiday(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return self.name
