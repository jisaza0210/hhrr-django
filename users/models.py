from datetime import date, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
import datetime


class VacationRequest(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pendiente"),
        ("APPROVED", "Aprobada"),
        ("REJECTED", "Rechazada"),
    ]

    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    end_date = models.DateField()
    message = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    backup_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="backup_person",
        help_text="La persona que va a quedar a cargo de tus funciones mientras estás de vacaciones",
    )
    compensatory_days = models.IntegerField(
        default=0,
        help_text="De los días solicitados, cuántos son compensatorios",
    )

    def __str__(self):
        return f"{self.employee.first_name}'s vacation ({self.start_date} to {self.end_date})"


class Employee(models.Model):
    birthdate = models.DateField(default=datetime.date.today)
    role = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(default=date.today)  # Employee's start date
    team = models.ForeignKey("Team", on_delete=models.SET_NULL, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vacation_days_taken = models.IntegerField(default=0)  # Days already taken

    def get_total_vacation_days(self):
        today = date.today()
        years_worked = today.year - self.start_date.year
        return 15 * years_worked

    def calculate_available_vacation_days(self):
        today = date.today()
        total_vacation_days = self.get_total_vacation_days()

        # Prorated days for the first year
        if today.year == self.start_date.year:
            days_worked = (today - self.start_date).days
            total_vacation_days = int((15 / 365) * days_worked)

        # Fetch approved vacation days excluding holidays
        approved_vacation_days = self.get_approved_vacation_days()

        # Calculate available vacation days
        available_days = total_vacation_days - approved_vacation_days
        return max(available_days, 0)

    def get_approved_vacation_days(self):
        """Calculate the total number of approved vacation days, excluding holidays."""
        # Fetch approved vacation requests for this employee
        approved_requests = VacationRequest.objects.filter(
            employee=self.user, status="APPROVED"
        )

        # Fetch all holidays from the database
        holidays = Holiday.objects.values_list("date", flat=True)

        # Calculate total days excluding holidays
        total_days = 0
        for request in approved_requests:
            current_date = request.start_date
            while current_date <= request.end_date:
                if (
                    current_date not in holidays and current_date.weekday() < 5
                ):  # Exclude holidays and weekends
                    total_days += 1
                current_date += timedelta(days=1)

            total_days -= request.compensatory_days

        return total_days

    def __str__(self):
        return self.user.username


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    approvers = models.ManyToManyField(User, related_name="approver_teams")

    def __str__(self):
        return self.name


class Holiday(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return self.name
