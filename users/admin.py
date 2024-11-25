from django.contrib import admin
from .models import Team, Employee, Holiday, VacationRequest

admin.site.register(Employee)
admin.site.register(Holiday)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name",)
    filter_horizontal = ("approvers",)


@admin.register(VacationRequest)
class VacationRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "start_date", "end_date", "status", "created_at")
