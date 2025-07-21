from celery import shared_task
from .models import ExcelFile, NarrationEntry
import pandas as pd
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_excel_file(excel_file_id):
    excel_file_instance = ExcelFile.objects.get(id=excel_file_id)
    try:
        df = pd.read_excel(excel_file_instance.file.path)
        entries = [
            NarrationEntry(
                excel_file=excel_file_instance,
                narration=str(row['Narration']),
                has_Credit=bool(pd.notnull(row['Credit']) and pd.isnull(row['Debit']))
            )
            for _, row in df.iterrows() if pd.notnull(row['Narration'])
        ]
        NarrationEntry.objects.bulk_create(entries)
        logger.info(f"Successfully processed file: {excel_file_instance.file.name}")
    except Exception as e:
        excel_file_instance.delete()
        logger.error(f"Error processing file {excel_file_instance.file.name}: {str(e)}")
        raise