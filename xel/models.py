from django.db import models

class ExcelFile(models.Model):
    file = models.FileField(upload_to='excel_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.status}"

class NarrationEntry(models.Model):
    excel_file = models.ForeignKey(ExcelFile, on_delete=models.CASCADE)
    narration = models.TextField()
    has_Credit = models.BooleanField(default=False)

    def __str__(self):
        return self.narration