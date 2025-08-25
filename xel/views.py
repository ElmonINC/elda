from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.views import generic
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from django.contrib.auth import logout as auth_logout, authenticate, login
from django.views.decorators.http import require_POST
from .forms import NarrationSearchForm, ExcelUploadForm
from .models import ExcelFile, NarrationEntry, UserProfile
from .utils import generate_pdf
from django.db.models import Q
import logging
import time
from .task import process_excel_file
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

def is_admin(user):
    return hasattr(user, 'userprofile') and user.userprofile.is_admin

@require_GET
def health_check(request): # Simple health check endpoint to verify that the service is running
    """
    Simple health check endpoint to verify that the service is running. 
    """
    return JsonResponse({"Status": "OK", "service": "elda"}, status=200)

class RegisterView(generic.CreateView): # View to handle user registration
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/register.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        UserProfile.objects.create(user=self.object, is_admin=False)  # Create UserProfile for new user
        return response

def index(request): # View to render the index page
    return redirect('search_narration')

def admin_login(request):
    error = None    # View to handle admin login
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and hasattr(user, 'userprofile') and user.userprofile.is_admin:
            login(request, user)
            return redirect('admin_xel')
        else:
            error = "Invalid credentials or not an admin."
    return render(request, 'xel/admin_login.html', {'error': error})

@login_required
def logout(request): # View to log out the user
    auth_logout(request)
    return redirect('index')

@user_passes_test(is_admin)
def admin_xel(request): # View to manage uploaded Excel files
    files = ExcelFile.objects.all()
    upload_form = ExcelUploadForm()
    if request.method == 'POST':
        upload_form = ExcelUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            excel_file_instance = upload_form.save()
            # Trigger Celery task to process the file
            process_excel_file.delay(excel_file_instance.id)
            return render(request, 'xel/admin.html', {
                'files': files,
                'upload_form': upload_form,
                'message': 'File uploaded successfully and is being processed.'
            })
    return render(request, 'xel/admin.html', {
        'files': files,
        'upload_form': upload_form
    })

@login_required
def search_narration(request):
    show_results = False
    form = NarrationSearchForm()
    results = []
    query = ''
    if request.method == 'POST':
        form = NarrationSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query'].strip()
            query_words = query.lower().split()
            if 2 <= len(query_words) <= 3:
                cache_key = f"search_{query.lower().replace(' ', '_')}"
                start_time = time.time()
                results = cache.get(cache_key)
                if results is None:
                    query_filter = Q(has_credit=True)
                    for word in query_words:
                        query_filter &= Q(narration__icontains=word)
                    entries = NarrationEntry.objects.filter(query_filter)
                    results = []
                    for entry in entries:
                        narration = entry.narration or ""
                        person = narration.split('by', 1)[1].strip() if 'by' in narration.lower() else narration
                        if person:
                            results.append({
                                'id': entry.id,
                                'person': person,
                                'narration': narration,
                                'credit': entry.credit,
                                'account_name': entry.account_name,
                                'financial_date': entry.financial_date,
                                'nuban': entry.nuban
                            })
                    results = sorted(results, key=lambda x: x['person'].lower())
                    results = [{'number': i+1, **result} for i, result in enumerate(results)]
                    cache.set(cache_key, results, timeout=3600)
                    logger.info(f"Search query: {query}, Results: {len(results)}, Time: {time.time() - start_time:.2f} seconds")
                else:
                    logger.info(f"Cache hit for query: {query}, Time: {time.time() - start_time:.2f} seconds")
                show_results = True

    # Add pagination
    paginator = Paginator(results, 5)  # Show 5 results per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'xel/search.html', {
        'form': form,
        'results': page_obj,
        'query': query,
        'show_results': show_results,
        'page_obj': page_obj,
    })

@login_required 
def generate_pdf_view(request, narration_id): # View to generate PDF for a specific narration entry
    try:
        entry = NarrationEntry.objects.get(id=narration_id)
        # Ensure user has access (e.g., admin or entry is public)
        if not (hasattr(request.user, 'userprofile') and request.user.userprofile.is_admin):
            # Add logic here if entries are tied to users; for now, allow all logged-in users
            pass
        data = {
            'narration': entry.narration,
            'credit': entry.credit,
            'account_name': entry.account_name,
            'financial_date': entry.financial_date,
            'nuban': entry.nuban
        }
        pdf = generate_pdf(data)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="result_{narration_id}.pdf"'
        response.write(pdf)
        return response
    except NarrationEntry.DoesNotExist:
        logger.error(f"NarrationEntry with id {narration_id} not found")
        return render(request, 'xel/error.html', {
            'error_message': 'The requested entry was not found.',
        }, status=404)