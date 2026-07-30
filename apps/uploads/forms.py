from django import forms
from .services import validate_file

class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='Select File',
        help_text='Maximum file size: 10MB. Allowed formats: CSV, XLSX.'
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            validate_file(file)
        return file