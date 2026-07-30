from django.urls import path
from . import views

app_name = 'influencers'

urlpatterns = [
    path('nlp/', views.nlp_processing_view, name='nlp_dashboard'),
    path('ai-classification/', views.ai_classification_view, name='ai_classification'),
]