# Create your views here.
from django.shortcuts import render, redirect
from .forms import UploadFileForm
from django.db.models import Q
from django.http import JsonResponse
from .models import SearchModel
from .utils import extract_text
import os
import logging
from django.conf import settings
import pandas as pd

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'data_elda/index.html')

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            uploaded_file = request.FILES['file']
            
            # Create the uploads directory if it doesn't exist
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_dir, uploaded_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks(chunk_size=8192):
                    destination.write(chunk)
            
            # Process Excel file if applicable
            content = ""
            if uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, engine='openpyxl')
                content = df.to_json()
            
            # Save to database
            document = SearchModel.objects.create(
                file=f'uploads/{uploaded_file.name}',
                content=content
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'File uploaded successfully',
                'file_id': document.id
            })
            
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'No file provided'
    }, status=400)

def search(request):
    query = request.GET.get('q', '')
    if query:
        results = SearchModel.objects.filter(
            Q(content__icontains=query) |
            Q(file__icontains=query)
        )
    else:
        results = []
    return render(request, 'data_elda/se-res.html', {
        'results': results,
        'query': query
    })