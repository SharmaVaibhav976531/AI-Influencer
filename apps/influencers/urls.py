from django.urls import path
from . import views

app_name = 'influencers'

urlpatterns = [
    path('nlp/', views.nlp_processing_view, name='nlp_dashboard'),
    path('ai-classification/', views.ai_classification_view, name='ai_classification'),
    path('ai-classification/stream/', views.ai_classification_stream_view, name='ai_classification_stream'),

    path('results/', views.results_list_view, name='results_list'),
    path('results/<int:pk>/', views.influencer_detail_view, name='influencer_detail'),
    path('results/export/', views.export_results_view, name='export_results'),
    path('discovery/', views.discovery_view, name='discovery'),
]