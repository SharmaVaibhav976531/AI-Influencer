from django.urls import path
from . import views

app_name = 'uploads'

urlpatterns = [
    path('', views.upload_view, name='upload'),
    path('history/', views.upload_history_view, name='history'),
    path('preview/<int:pk>/', views.upload_preview_view, name='preview'),
]