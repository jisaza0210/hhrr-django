from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Employee
from django.contrib.auth.models import User


def home_page(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"¡Hola {user.first_name}! Bienvenidx de nuevo")
            return redirect("home")

        messages.error(
            request,
            "Usuario o contraseña equivocados. Por favor, revisa tus credenciales, e intenta de nuevo",
        )
        return redirect("home")

    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        employee = Employee.objects.get(id=user.id)
        available_days = employee.calculate_available_vacation_days()
        user_team = user.employee.team
        employees_in_team = Employee.objects.filter(team=user_team).exclude(user=user)
    else:
        employees_in_team = None
        available_days = None

    context = {}
    context["employees_in_team"] = employees_in_team
    context["available_days"] = available_days
    return render(request, "home_page.html", context)


def logout_user(request):
    logout(request)
    messages.success(request, "Has cerrado sesión de manera éxitosa")
    return redirect("home")
