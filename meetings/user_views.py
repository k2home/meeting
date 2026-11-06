from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import SetPasswordForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ManagedUserChangeForm, ManagedUserCreationForm

User = get_user_model()


def _is_admin(user):
    return user.is_authenticated and user.is_staff


def _cannot_remove_last_admin(target, active, staff):
    if target.is_staff and target.is_active and (not active or not staff):
        return not User.objects.filter(is_staff=True, is_active=True).exclude(pk=target.pk).exists()
    return False


@login_required
@user_passes_test(_is_admin)
def user_list(request):
    users = User.objects.order_by("username")
    query = request.GET.get("q", "").strip()
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
        )
    return render(request, "meetings/user_list.html", {"users": users, "query": query})


@login_required
@user_passes_test(_is_admin)
def user_create(request):
    form = ManagedUserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"Benutzerkonto „{user.username}“ wurde angelegt.")
        return redirect("user_list")
    return render(request, "meetings/user_form.html", {"form": form, "heading": "Benutzer anlegen"})


@login_required
@user_passes_test(_is_admin)
def user_edit(request, pk):
    target = get_object_or_404(User, pk=pk)
    if target.is_superuser and not request.user.is_superuser:
        messages.error(request, "Superuser-Konten können hier nur von Superusern geändert werden.")
        return redirect("user_list")

    form = ManagedUserChangeForm(request.POST or None, instance=target)
    if request.method == "POST" and form.is_valid():
        active = form.cleaned_data["is_active"]
        staff = form.cleaned_data["is_staff"]
        if target.pk == request.user.pk and (not active or not staff):
            form.add_error(None, "Das eigene Konto kann nicht deaktiviert oder seiner Administratorrechte beraubt werden.")
        elif _cannot_remove_last_admin(target, active, staff):
            form.add_error(None, "Der letzte aktive Administrator kann nicht deaktiviert oder herabgestuft werden.")
        else:
            form.save()
            messages.success(request, f"Benutzerkonto „{target.username}“ wurde aktualisiert.")
            return redirect("user_list")
    return render(request, "meetings/user_form.html", {
        "form": form, "heading": f"Benutzer bearbeiten: {target.username}", "target": target,
    })


@login_required
@user_passes_test(_is_admin)
def user_password(request, pk):
    target = get_object_or_404(User, pk=pk)
    if target.is_superuser and not request.user.is_superuser:
        messages.error(request, "Das Passwort eines Superusers kann hier nicht geändert werden.")
        return redirect("user_list")
    form = SetPasswordForm(target, request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Passwort für „{target.username}“ wurde zurückgesetzt.")
        return redirect("user_list")
    return render(request, "meetings/user_password.html", {"form": form, "target": target})
