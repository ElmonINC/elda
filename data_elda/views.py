# Create your views here.
from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import UploadedFile
from .utils import extract_text
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank



def index(request):
    return render(request, 'data_elda/index.html')

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            file_path = uploaded_file.file.path
            text = extract_text(file_path)
            uploaded_file.content = text
            uploaded_file.save()
            return redirect('index')  # Redirect back to the main page
    else:
        form = UploadFileForm()
    return render(request, 'index.html', {'form': form})

def search(request):
    query = request.GET.get('q')
    if query:
        search_query = SearchQuery(query, search_type='websearch')
        results = UploadedFile.objects.annotate(
            rank=SearchRank(SearchVector('content', 'file'), search_query)
        ).filter(rank__gte=0.1).order_by('-rank')
    else:
        results = UploadedFile.objects.none()
    return render(request, 'search_results.html', {'results': results, 'query': query})