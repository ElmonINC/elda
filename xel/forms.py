from django import forms
from .models import ExcelFile
import pandas as pd

class NarrationSearchForm(forms.Form):
    query = forms.CharField(label="Enter name to search", max_length=255)

    def clean_query(self):
        query = self.cleaned_data['query'].strip()
        words = query.split()
        if len(words) not in [2, 3]:
            raise forms.ValidationError("Query must be 2 or 3 words")
        return query

class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = ExcelFile
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file.name.endswith(('.xlsx', '.xls')):
            raise forms.ValidationError("File must be an Excel file (.xlsx or .xls)")
        try:
            df = pd.read_excel(file, dtype_backend='numpy_nullable')
            if 'Narration' not in df.columns:
                raise forms.ValidationError("The uploaded file must contain a 'Narration' column")
        except Exception as e:
            raise forms.ValidationError(f"Error reading Excel file: {str(e)}")
        return file