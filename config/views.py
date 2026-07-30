from django.shortcuts import render

def custom_404_view(request, exception=None):
    """
    Custom 404 error handler view.
    Renders templates/404.html with HTTP status code 404.
    """
    return render(request, '404.html', status=404)

def custom_500_view(request, exception=None):
    """
    Custom 500 error handler view.
    Renders templates/500.html with HTTP status code 500.
    """
    return render(request, '500.html', status=500)
