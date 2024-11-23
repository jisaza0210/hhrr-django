from django.contrib import admin
from .models import Team, Employee, Holiday, VacationRequest

admin.site.register(Team)
admin.site.register(Employee)
admin.site.register(Holiday)
admin.site.register(VacationRequest)
