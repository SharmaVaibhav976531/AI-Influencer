from django.urls import path
from django.views.generic import TemplateView
from .views import CustomLoginView, custom_logout_view, SignUpView

urlpatterns = [
    # Authentication
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    
    # Informational Forgot Password Page (No email/token processing)
    path('forgot-password/', TemplateView.as_view(template_name='authentication/forgot_password.html'), name='forgot_password'),
]