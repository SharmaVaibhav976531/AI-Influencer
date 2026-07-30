from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def home_view(request):
    """Render the main dashboard homepage. Protected by @login_required."""
    context = {
        'page_title': 'Dashboard Overview'
    }
    return render(request, 'dashboard/home.html', context)