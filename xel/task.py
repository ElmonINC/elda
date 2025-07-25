from celery import shared_task
import pandas as pd
from .models import ExcelFile, NarrationEntry
import logging
import os

logger = logging.getLogger(__name__)

@shared_task
def process_excel_file(file_id):
    try:
        excel_file = ExcelFile.objects.get(id=file_id)
        file_path = excel_file.file.path
        df = pd.read_excel(file_path, parse_dates=['Transaction Date', 'Financial Date'], dtype_backend='numpy_nullable')
        if 'Narration' not in df.columns:
            excel_file.delete()
            raise ValueError("Excel file must contain a 'Narration' column")
        entries = []
        for _, row in df.iterrows():
            entries.append(NarrationEntry(
                excel_file=excel_file,
                debit=float(row.get('Debit', 0) or 0),
                credit=float(row.get('Credit', 0) or 0),
                entry_code=str(row.get('Entry Code', '')),
                instrument_no=str(row.get('Instrument No.', '')),
                client_ip_address=str(row.get('Client IP Address', '')),
                narration=str(row.get('Narration', '')),
                branch=str(row.get('Branch', '')),
                nuban=str(row.get('NUBAN', '')),
                account_name=str(row.get('Account Name', '')),
                teller=str(row.get('Teller', '')),
                transaction_date=row.get('Transaction Date'),
                financial_date=row.get('Financial Date'),
                has_credit=float(row.get('Credit', 0) or 0) > 0
            ))
        NarrationEntry.objects.bulk_create(entries)
        logger.info(f"Successfully processed file: {file_path}, ID: {file_id}")
        os.remove(file_path)
        excel_file.delete()
    except Exception as e:
        logger.error(f"Error processing file ID {file_id}: {str(e)}")
        if ExcelFile.objects.filter(id=file_id).exists():
            ExcelFile.objects.get(id=file_id).delete()
        raise