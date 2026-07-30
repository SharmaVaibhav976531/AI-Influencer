from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CustomLoginView, custom_logout_view, SignUpView
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

urlpatterns = [
    # Authentication
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),
    
    # Password Reset Flow
    path('forgot-password/', auth_views.PasswordResetView.as_view(
        template_name='authentication/forgot_password.html',
        form_class=CustomPasswordResetForm
    ), name='password_reset'),
    
    path('forgot-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='authentication/forgot_password_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='authentication/reset_confirm.html',
        form_class=CustomSetPasswordForm
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='authentication/reset_complete.html'
    ), name='password_reset_complete'),
]