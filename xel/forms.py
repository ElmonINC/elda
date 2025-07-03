# xel/forms.py
from django import forms
from .models import ExcelFile

class NarrationSearchForm(forms.Form):
    query = forms.CharField(label="Enter name to search", max_length=255)

class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = ExcelFile
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.endswith(('.xlsx', '.xls')):
            raise forms.ValidationError("Only Excel files are allowed.")
        return file