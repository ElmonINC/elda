# xel/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
import pandas as pd
from .models import ExcelFile, NameEntry

@receiver(post_save, sender=ExcelFile)
def process_excel_file(sender, instance, created, **kwargs):
    if created:
        try:
            df = pd.read_excel(instance.file.path)
            headers = {col.lower().strip(): col for col in df.columns}
            required_cols = ['first name', 'last name', 'status']
            if not all(col in headers for col in required_cols):
                print("Error: Excel file missing required columns: 'First Name', 'Last Name', 'Status'")
                return

            for index, row in df.iterrows():
                first_name = str(row[headers['first name']]).strip()
                last_name = str(row[headers['last name']]).strip()
                status = str(row[headers['status']]).strip()
                NameEntry.objects.create(
                    excel_file=instance,
                    first_name=first_name,
                    last_name=last_name,
                    status=status
                )
        except Exception as e:
            print(f"Error processing Excel file: {e}")
# Ensure that the ExcelFile model is imported correctly
# Ensure that the NameEntry model is imported correctly 