from django.db import models

class ExcelFile(models.Model):
    file = models.FileField(upload_to='excel_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class NarrationEntry(models.Model):
    excel_file = models.ForeignKey(ExcelFile, on_delete=models.CASCADE)
    narration = models.TextField(db_index=True)
    has_Credit = models.BooleanField(default=False, db_index=True)
    debit = models.CharField(max_length=255, blank=True)
    credit = models.CharField(max_length=255, blank=True)
    entry_code = models.CharField(max_length=255, blank=True)
    instrument_no = models.CharField(max_length=255, blank=True)
    client_ip_address = models.CharField(max_length=255, blank=True)
    branch = models.CharField(max_length=255, blank=True)
    nuban = models.CharField(max_length=255, blank=True)
    account_name = models.CharField(max_length=255, blank=True)
    teller = models.CharField(max_length=255, blank=True)
    transaction_date = models.CharField(max_length=255, blank=True)
    financial_date = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.narration

    class Meta:
        indexes = [
            models.Index(fields=['narration', 'has_Credit']),
        ]