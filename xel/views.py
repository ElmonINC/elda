from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse, HttpResponse
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
import pandas as pd
import logging
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
            return redirect('login')  # Redirect to login page after registration
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def logout(request):
    auth_logout(request)  # Use Django's built-in logout function
    return redirect('index')

def admin_login(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin')  # Redirect to your admin content page
        else:
            error = "Invalid credentials or not an admin."
    return render(request, 'xel/admin_login.html', {'error': error})

def handle_uploaded_file(excel_file_instance):
    try:
        df = pd.read_excel(excel_file_instance.file.path)
        entries = [
            NarrationEntry(excel_file=excel_file_instance, narration=str(narration))
            for narration in df['Narration'].dropna().tolist()
        ] 
        NarrationEntry.objects.bulk_create(entries)
        logger.info(f"Successfully processed file: {excel_file_instance.file.name}")
    except ValueError as e:
        excel_file_instance.delete()  # Rollback if error occurs
        raise ValueError(f"Error processing file {excel_file_instance.file.name}: {str(e)}")
    except Exception as e:
        excel_file_instance.delete()  # Rollback if error occurs
        raise Exception(f"An unexpected error occurred while processing file {excel_file_instance.file.name}: {str(e)}")

def read_excel_file(file_path):
    df = pd.read_excel(file_path, header=None)
    header_row = None
    for idx, row in df.iterrows():
        if "Narration" in row.values:
            header_row = idx
            break
    if header_row is not None:
        raise ValueError(f"The excil file must have a header row with the name 'Narration' .")
    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True) # Skip the header row

@login_required
def search_narration(request):
    results = []
    query = ""
    show_results = False
    if request.method == 'POST':
        form = NarrationSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query'].strip()
            query_words = query.lower().split()
            for entry in NarrationEntry.objects.all():
                narration_text = entry.narration or ""
                narration_lower = narration_text.lower()
                # Check if all query words are present or similar in the narration cell
                match_count = 0
                for word in query_words:
                    if word in narration_lower or SequenceMatcher(None, word, narration_lower).ratio() > 0.7:
                        match_count += 1
                if match_count == len(query_words):
                    results.append(entry) # Add the narration text to results if it matches the query
            # Remove duplicates, sort alphabetically
            seen = set()
            new_results = [r for r in results if not (r.narration in seen or seen.add(r.narration))]
            results = sorted(new_results, key=lambda x: x.narration.lower())
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
            handle_uploaded_file(excel_file_instance)
            return redirect('admin') # Redirect to the admin page after successful upload
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

def generate_pdf(request, narration_id):
    #Get the narration entry by ID
    naration = get_object_or_404(NarrationEntry, id=narration_id)
    excel_file = naration.excel_file

    #Read the Excel file to get the narration
    df = pd.read_excel(excel_file.file.path)
    row = df[df['Narration'] == naration.narration].iloc[0]

    #Define where to place each field on the image (x, y coordinates fromt the top left corner, in pixels)
    field_position = {
        'Financial Date': (246, 212),  #Date
        'Narration': (50, 100),  # Depositor's Name
        'Narration': (780, 105), #Department and Level
        'Credit': (1947, 397), #Amount in Figures
        'Credit': (1980, 1023), # Total amount in Figures
    }
   
   #Locate the image template
    image_path = finders.find('xel/image/Teller.png')
    if not image_path:
        return HttpResponse("Image template not found.", status=404)
    
    #Get image dimensions
    with Image.open(image_path) as img:
        width, height = img.size

    #Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{naration.narration}.pdf"'

    #Create canvas with page size matching the image dimensions
    c = canvas.Canvas(response, pagesize=(width, height))

    #Draw the image on the canvas
    c.drawImage(image_path, 0, 0, width=width, height=height)

    #Set the text proterties
    c.setFont("Helvetica", 32)
    c.setFillColor(colors.blue)

    #Overlay the texts from the Excel file onto the image
    for field, (x, y_from_top) in field_position.items():
        value = str(row[field]) if field in row else "N/A" # Default to "N/A" if field not found
        #Convert y_from_top to PDF coordinate system (origin at bottom left)
        y_pdf = height - y_from_top
        c.drawString(x, y_pdf, f"{field}: {value}")

    #Save and print the PDF
    c.showPage()
    c.save()
    return response