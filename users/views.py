from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def home_page(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            messages.success(request, "¡Hola chacarerx! Bienvenidx de nuevo")
            return redirect("home")

        messages.error(
            request,
            "Usuario o contraseña equivocados. Por favor, revisa tus credenciales, e intenta de nuevo",
        )
        return redirect("home")

    context = {}
    return render(request, "home_page.html", context)


def logout_user(request):
    logout(request)
    messages.success(request, "Has cerrado sesión de manera éxitosa")
    return redirect("home")
