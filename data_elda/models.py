from django.db import models
from django.utils.text import slugify
import os

class SearchModel(models.Model):
    """
    Model to store uploaded files and their extracted content.
    """
    file = models.FileField(upload_to='uploads/')
    original_filename = models.CharField(max_length=255, default="unknown")
    file_type = models.CharField(max_length=100, default="unknown")
    file_size = models.IntegerField(default=0)  
    content = models.TextField(blank=True)
    preview_content = models.TextField(blank=True)  # For storing preview snippets
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.original_filename and self.file:
            self.original_filename = os.path.basename(self.file.name)
        if not self.file_type and self.file:
            self.file_type = os.path.splitext(self.file.name)[1].lower()
        if not self.file_size and self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.original_filename} ({self.file_type})"

    class Meta:
        ordering = ['-uploaded_at']
