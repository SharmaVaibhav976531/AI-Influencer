from django.shortcuts import render

def home_view(request):
    """Render the main dashboard homepage."""
    context = {
        'page_title': 'Dashboard Overview'
    }
    return render(request, 'dashboard/home.html', context)