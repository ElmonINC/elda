# xel/forms.py
from django import forms
from .models import ExcelFile
import pandas as pd

class NarrationSearchForm(forms.Form):
    query = forms.CharField(label="Enter name to search", max_length=255)

class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = ExcelFile
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            try:
                df = pd.read_excel(file)
                if 'Narration' not in df.columns:
                    raise forms.ValidationError("The uploaded file must contain a 'Narration' column.")
            except Exception as e:
                raise forms.ValidationError(f"Error reading Excel file: {str(e)}")
        return file
    
