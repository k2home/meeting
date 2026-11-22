from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def user_guide(request):
    """Role-independent user documentation for all authenticated users."""
    return render(request, "meetings/user_guide.html")
