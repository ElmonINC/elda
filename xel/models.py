from django.db import models
from django.contrib.auth.models import User

class ExcelFile(models.Model):
    file = models.FileField(upload_to='excel_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class NarrationEntry(models.Model):
    excel_file = models.ForeignKey(ExcelFile, on_delete=models.CASCADE)
    narration = models.TextField(db_index=True)
    has_credit = models.BooleanField(default=False, db_index=True)
    debit = models.DecimalField(max_digits=255, decimal_places=2, default=0.00, blank=True)
    credit = models.DecimalField(max_digits=255, decimal_places=2, default=0.00, blank=True)
    entry_code = models.CharField(max_length=255, blank=True)
    instrument_no = models.CharField(max_length=255, blank=True)
    client_ip_address = models.CharField(max_length=255, blank=True)
    branch = models.CharField(max_length=255, blank=True)
    nuban = models.CharField(max_length=255, blank=True)
    account_name = models.CharField(max_length=255, blank=True)
    teller = models.CharField(max_length=255, blank=True)
    transaction_date = models.DateTimeField(null=True, blank=True)
    financial_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.narration

    class Meta:
        indexes = [
            models.Index(fields=['narration', 'has_credit']),
        ]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Admin' if self.is_admin else 'User'}"