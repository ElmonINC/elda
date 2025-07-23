from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from django.contrib.auth import logout as auth_logout, authenticate
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST
from django.contrib.staticfiles import finders
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from PIL import Image
from .forms import NarrationSearchForm, ExcelUploadForm
from .models import ExcelFile, NarrationEntry
from .task import process_excel_file
from django.db.models import Q
import pandas as pd
import logging
import re
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class RegisterView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

def index(request):
    return render(request, 'xel/index.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def logout(request):
    auth_logout(request)
    return redirect('index')

def admin_login(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin')
        else:
            error = "Invalid credentials or not an admin."
    return render(request, 'xel/admin_login.html', {'error': error})

#def handle_uploaded_file(excel_file_instance):
#    try:
#        df = pd.read_excel(excel_file_instance.file.path)
#        entries = [
#            NarrationEntry(excel_file=excel_file_instance,
#                narration=str(row['Narration']),
#                has_Credit=bool(pd.notnull(row['Credit']) and pd.isnull(row['Debit'])),
#                financial_date=str(row['Financial Date']) if pd.notnull(row.get('Financial Date')) else "",
#                credit=str(row['Credit']) if pd.notnull(row.get('Credit')) else ""
#            )
#            for _, row in df.iterrows() if pd.notnull(row['Narration'])
#        ]
#        NarrationEntry.objects.bulk_create(entries)
#        logger.info(f"Successfully processed file: {excel_file_instance.file.name}")
#    except KeyError as e:
#        excel_file_instance.delete()
#        raise ValueError(f"Missing required column in {excel_file_instance.file.name}: {str(e)}")
#    except Exception as e:
#        excel_file_instance.delete()
#        raise Exception(f"An unexpected error occurred while processing file {excel_file_instance.file.name}: {str(e)}")
    
def read_excel_file(file_path):
    df = pd.read_excel(file_path, header=None)
    header_row = None
    for idx, row in df.iterrows():
        if "Narration" in row.values:
            header_row = idx
            break
    if header_row is not None:
        raise ValueError(f"The excel file must have a header row with the name 'Narration'.")
    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

@login_required
def search_narration(request):
    results = []
    query = ""
    show_results = False
    if request.method == 'POST':
        form = NarrationSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query'].strip()
            cache_key = f"search_{query.lower().replace(' ', '_')}"
            results = cache.get(cache_key)
            if results is None:
                query_words = query.lower().split()
                query_filter = Q()
                for word in query_words:
                    query_filter &= Q(narration__icontains=word)
                entries = NarrationEntry.objects.filter(has_Credit=True).filter(query_filter)[:100]
                results = []
                for entry in entries:
                    narration_text = entry.narration or ""
                    narration_lower = narration_text.lower()
                    match_count = 0
                    for word in query_words:
                        if word in narration_lower:
                            match_count += 1
                        elif SequenceMatcher(None, word, narration_lower).ratio() > 0.7:
                            match_count += 1
                    if match_count == len(query_words):
                        results.append(entry)
                seen = set()
                unique_results = [r for r in results if not (r.narration in seen or seen.add(r.narration))]
                results = sorted(unique_results, key=lambda x: x.narration.lower())
                cache.set(cache_key, results, timeout=3600)  # Cache for 1 hour
                logger.info(f"Search query '{query}', Results: {len(results)}, Time: {time.time() - start_time:.2f}seconds")
            else:
                logger.info(f"Cache hit for query '{query}', Time: {time.time() - start_time:.2f} seconds")
            show_results = True
    else:
        form = NarrationSearchForm()
    return render(request, 'xel/search.html', {
        'form': form,
        'results': results,
        'query': query,
        'show_results': show_results,
    })

@user_passes_test(lambda u: u.is_superuser)
def admin_xel(request):
    files = ExcelFile.objects.all()
    if request.method == 'POST':
        upload_form = ExcelUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            excel_file_instance = upload_form.save()
            logger.info(f"File uploaded: {excel_file_instance.file.name}, ID: {excel_file_instance.id}") # Log the file upload
            process_excel_file.delay(excel_file_instance.id)  # Run in background
            logger.info(f"Processing task for file ID: {excel_file_instance.id} has been queued.")
            return redirect('admin')
        else:
            logger.error(f"File upload failed: {upload_form.errors}")
            #return render(request, 'xel/admin.html', {'files': files, 'upload_form': upload_form, 'errors': upload_form.errors})
    else:
        upload_form = ExcelUploadForm()
    return render(request, 'xel/admin.html', {
        'files': files,
        'upload_form': upload_form,
    })

@user_passes_test(lambda u: u.is_superuser)
@require_POST
def delete_excel_file(request, file_id):
    logger.debug(f"Attempting to delete file with ID: {file_id}")
    file = get_object_or_404(ExcelFile, id=file_id)
    file.delete()
    logger.debug(f"File with ID: {file_id} deleted successfully.")
    return JsonResponse({'success': True, 'file_id': file_id})

@login_required
def generate_pdf(request, narration_id):
    narration = get_object_or_404(NarrationEntry, id=narration_id)
    logger.info(f"Generating PDF for narration ID: {narration_id}, Narration: {narration.narration}")
    field_position = {
        'Financial Date': [(246, 212)],
        'Narration': [(50, 100), (780, 105)],
        'Credit': [(1947, 397), (1980, 1023)],
    }
    image_path = finders.find('xel/image/Teller.png')
    if not image_path:
        return HttpResponse("Image template not found.", status=404)
    
    with Image.open(image_path) as img:
        width, height = img.size

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{narration.narration}.pdf"'

    c = canvas.Canvas(response, pagesize=(width, height))
    c.drawImage(image_path, 0, 0, width=width, height=height)

    c.setFont("Helvetica", 32)
    c.setFillColor(colors.blue)

    for field, positions in field_position.items():
        if field == 'Narration':
            value = narration.narration or "N/A"
            match = re.match(r'^(.*?)\bby\b\s*([^()]+)\s*\((.*?)\)$', value)
            if match:
                narration_parts = [match.group(2).strip(), match.group(3)]
            else:
                narration_parts = ["", ""]
            for i, (x, y_from_top) in enumerate(positions):
                part = narration_parts[i] if i < len(narration_parts) else ""
                y_pdf = height - y_from_top
                c.drawString(x, y_pdf, part)
        else:
            value = getattr(narration, field.lower().replace(" ", "_"), "N/A")
            for x, y_from_top in positions:
                y_pdf = height - y_from_top
                c.drawString(x, y_pdf, str(value))

    c.showPage()
    c.save()
    return response