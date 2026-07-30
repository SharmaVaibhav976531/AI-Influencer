from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView

from .forms import CustomLoginForm, CustomUserCreationForm


class CustomLoginView(LoginView):
    """Handles user login with custom form and 'Remember Me' logic."""
    
    template_name = 'authentication/login.html'
    form_class = CustomLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('dashboard:home')

    def form_valid(self, form):
        """Process valid login and handle session expiry based on 'Remember Me'."""
        response = super().form_valid(form)
        if not form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)
        return response

    def form_invalid(self, form):
        """Display a generic error message for invalid credentials."""
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)

class SignUpView(CreateView):
    """Handles new user registration."""
    
    form_class = CustomUserCreationForm
    template_name = 'authentication/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Account created successfully! Please log in.")
        return response

@require_http_methods(["GET", "POST"])
def custom_logout_view(request):
    """Securely logs out the user and displays a success message."""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')