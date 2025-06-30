# xel/forms.py
from django import forms

class NameSearchForm(forms.Form):
    first_name = forms.CharField(max_length=255, label="First Name")
    last_name = forms.CharField(max_length=255, label="Last Name")

class ExcelUploadForm(forms.ModelForm):
    class Meta:
        model = None  # This should be set to your ExcelFile model
        fields = ['file']  # Assuming 'file' is the field for the uploaded file
        widgets = {
            'file': forms.ClearableFileInput(attrs={'multiple': False}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = True  # Make the file field required