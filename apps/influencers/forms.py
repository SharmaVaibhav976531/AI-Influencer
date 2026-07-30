from django import forms
from apps.influencers.models import Influencer
from apps.classification.models import Classification

class ResultFilterForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-sm', 'placeholder': 'Search...'
    }))
    
    platform = forms.ChoiceField(required=False, choices=[('', 'All Platforms')] + list(Influencer.Platform.choices))
    
    recommendation = forms.ChoiceField(required=False, choices=[('', 'All')] + list(Classification.Recommendation.choices))
    
    min_score = forms.IntegerField(required=False, min_value=0, max_value=100, widget=forms.NumberInput(attrs={
        'class': 'form-control form-control-sm', 'placeholder': '0'
    }))
    
    max_score = forms.IntegerField(required=False, min_value=0, max_value=100, widget=forms.NumberInput(attrs={
        'class': 'form-control form-control-sm', 'placeholder': '100'
    }))
    
    min_followers = forms.IntegerField(required=False, min_value=0, widget=forms.NumberInput(attrs={
        'class': 'form-control form-control-sm', 'placeholder': 'Min'
    }))
    
    max_followers = forms.IntegerField(required=False, min_value=0, widget=forms.NumberInput(attrs={
        'class': 'form-control form-control-sm', 'placeholder': 'Max'
    }))