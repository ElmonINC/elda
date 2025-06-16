from django.db import models

class UploadedFile(models.Model):
    """
    Model to store uploaded files.
    """
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True)

# Create your models here.
