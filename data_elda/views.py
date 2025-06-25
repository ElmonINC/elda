# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.conf import settings
from .forms import UploadFileForm
from .models import SearchModel
from .utils import extract_text, find_matches
import os
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)

def index(request):
    """Render the main page with upload form and search."""
    return render(request, 'data_elda/index.html')

@csrf_exempt
def upload_file(request):
    """Handle file uploads and process their content."""
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            uploaded_file = request.FILES['file']
            
            # Create the uploads directory if it doesn't exist
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_dir, uploaded_file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Extract text and generate preview
            full_text, preview_text = extract_text(file_path)
            
            # Save to database
            document = SearchModel.objects.create(
                file=f'uploads/{uploaded_file.name}',
                content=full_text,
                preview_content=preview_text
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'File uploaded and processed successfully',
                'file_id': document.id,
                'preview': preview_text
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
    """Handle search requests and return results with context."""
    query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)
    
    if not query:
        return render(request, 'data_elda/se-res.html', {
            'results': [],
            'query': '',
            'total_results': 0
        })
    
    # Search in both content and filename
    results = SearchModel.objects.filter(
        Q(content__icontains=query) |
        Q(original_filename__icontains=query)
    )
    
    # Add match information to each result
    for result in results:
        matches = find_matches(result.content, query)
        result.matches = matches[:5]  # Limit to 5 matches per file
    
    # Paginate results
    paginator = Paginator(results, 10)  # 10 results per page
    page_obj = paginator.get_page(page)
    
    return render(request, 'data_elda/se-res.html', {
        'results': page_obj,
        'query': query,
        'total_results': len(results)
    })

def preview_file(request, file_id):
    """Show full preview of a file."""
    document = get_object_or_404(SearchModel, id=file_id)
    return render(request, 'data_elda/preview.html', {
        'document': document
    })

def download_file(request, file_id):
    """Download the original file."""
    document = get_object_or_404(SearchModel, id=file_id)
    file_path = os.path.join(settings.MEDIA_ROOT, document.file.name)
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{document.original_filename}"'
            return response
    
    return HttpResponse('File not found', status=404)