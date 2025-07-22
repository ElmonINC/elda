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
                narration=str(row['Narration']) if pd.notnull(row.get('Narration')) else "",
                has_Credit=bool(pd.notnull(row.get('Credit')) and pd.isnull(row.get('Debit'))),
                debit=str(row['Debit']) if pd.notnull(row.get('Debit')) else "",
                credit=str(row['Credit']) if pd.notnull(row.get('Credit')) else "",
                entry_code=str(row['Entry Code']) if pd.notnull(row.get('Entry Code')) else "",
                instrument_no=str(row['Instrument No.']) if pd.notnull(row.get('Instrument No.')) else "",
                client_ip_address=str(row['Client IP Address']) if pd.notnull(row.get('Client IP Address')) else "",
                branch=str(row['Branch']) if pd.notnull(row.get('Branch')) else "",
                nuban=str(row['NUBAN']) if pd.notnull(row.get('NUBAN')) else "",
                account_name=str(row['Account Name']) if pd.notnull(row.get('Account Name')) else "",
                teller=str(row['Teller']) if pd.notnull(row.get('Teller')) else "",
                transaction_date=str(row['Transaction Date']) if pd.notnull(row.get('Transaction Date')) else "",
                financial_date=str(row['Financial Date']) if pd.notnull(row.get('Financial Date')) else ""
            )
            for _, row in df.iterrows() if pd.notnull(row.get('Narration'))
        ]
        NarrationEntry.objects.bulk_create(entries)
        logger.info(f"Successfully processed file: {excel_file_instance.file.name}")
    except KeyError as e:
        excel_file_instance.delete()
        logger.error(f"Missing required column in {excel_file_instance.file.name}: {str(e)}")
        raise
    except Exception as e:
        excel_file_instance.delete()
        logger.error(f"Error processing file {excel_file_instance.file.name}: {str(e)}")
        raise