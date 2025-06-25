# xel/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
import pandas as pd
from .models import ExcelFile, NameEntry

@receiver(post_save, sender=ExcelFile)
def process_excel_file(sender, instance, created, **kwargs):
    if created:
        df = pd.read_excel(instance.file.path)
        headers = {col.lower().strip(): col for col in df.columns}
        try:
            first_name_col = headers['first name']
            last_name_col = headers['last name']
            status_col = headers['status']
        except KeyError:
            print("Missing required columns: 'First Name', 'Last Name', 'Status'")
            return

        for index, row in df.iterrows():
            first_name = str(row[first_name_col]).strip()
            last_name = str(row[last_name_col]).strip()
            status = str(row[status_col]).strip()
            NameEntry.objects.create(
                excel_file=instance,
                first_name=first_name,
                last_name=last_name,
                status=status
            )