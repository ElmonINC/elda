from django import forms
from .models import SearchModel

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = SearchModel
        fields = ['file']