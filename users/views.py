from .forms import VacationRequestForm, VacationRequestUpdateForm
from .models import Employee, VacationRequest, Team
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render, get_object_or_404


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


@login_required
def request_vacation(request):
    if request.method == "POST":
        form = VacationRequestForm(request.POST, employee=request.user.employee)
        if form.is_valid():
            vacation_request = form.save(commit=False)
            vacation_request.employee = request.user  # Associate the logged-in user
            vacation_request.save()
            return redirect("vacations")  # Redirect to some page after saving
    else:
        form = VacationRequestForm(employee=request.user.employee)

    return render(request, "vacation_request.html", {"form": form})


@login_required
def user_vacation_requests(request):
    context = {}
    employee = Employee.objects.get(user_id=request.user.id)
    try:
        requests = VacationRequest.objects.filter(id=employee.id)
        context["requests"] = requests
    except ObjectDoesNotExist:
        context["requests"] = None

    return render(request, "user_vacation_requests.html", context)


@login_required
def team_vacation_requests(request):
    # Ensure user is an approver for at least one team
    teams = Team.objects.filter(approvers=request.user)
    if not teams.exists():
        messages.error(request, "No tienes acceso a esta sección.")
        return redirect("home")

    # Fetch vacation requests for all teams where the user is an approver
    requests = VacationRequest.objects.filter(employee__employee__team__in=teams)

    return render(request, "team_vacation_requests.html", {"requests": requests})


@login_required
def update_vacation_request(request, request_id):
    # Fetch the vacation request
    vacation_request = get_object_or_404(VacationRequest, id=request_id)

    # Ensure the user is an approver for the related team
    team = vacation_request.employee.employee.team
    if not team.approvers.filter(id=request.user.id).exists():
        messages.error(request, "No tienes permiso para modificar esta solicitud.")
        return redirect("team_vacation_requests")

    # Handle form submission
    if request.method == "POST":
        form = VacationRequestUpdateForm(request.POST, instance=vacation_request)
        if form.is_valid():
            form.save()
            messages.success(
                request, "El estado de la solicitud se ha actualizado correctamente."
            )
            return redirect("team_vacation_requests")
    else:
        form = VacationRequestUpdateForm(instance=vacation_request)

    return render(
        request,
        "update_vacation_request.html",
        {"form": form, "request_obj": vacation_request},
    )
