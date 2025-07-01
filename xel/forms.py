# xel/forms.py
from django import forms
from .models import ExcelFile

class NarrationSearchForm(forms.Form):
    query = forms.CharField(label="Search Narration", max_length=255)

class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = ExcelFile 
        fields = ['file']  # Assuming 'file' is the field for the uploaded file
        widgets = {
            'file': forms.ClearableFileInput(attrs={'multiple': False}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = True  # Make the file field required