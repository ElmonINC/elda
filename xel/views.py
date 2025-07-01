from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.views import generic
from .forms import NameSearchForm, ExcelUploadForm
from .models import NameEntry, ExcelFile, NarrationEntry
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login
import pandas as pd
from difflib import SequenceMatcher


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


@login_required
def search_name(request):
    if request.method == 'POST':
        form = NameSearchForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name'].strip()
            last_name = form.cleaned_data['last_name'].strip()
            search_term = f"{first_name} {last_name}".strip()

            # Narration similarity search
            narration_results = []
            for entry in NarrationEntry.objects.all():
                ratio = SequenceMatcher(None, search_term.lower(), entry.narration.lower()).ratio()
                if search_term.lower() in entry.narration.lower() or ratio > 0.5:
                    narration_results.append((entry, ratio))
            narration_results.sort(key=lambda x: x[1], reverse=True)
            narration_results = [entry for entry, _ in narration_results]

            entries = NameEntry.objects.filter(
                first_name__iexact=first_name,
                last_name__iexact=last_name
            )
            context = {
                'form': form,
                'entries': entries,
                'searched': True,
                'first_name': first_name,
                'last_name': last_name,
                'narration_results': narration_results,
            }
            return render(request, 'xel/search.html', context)
    else:
        form = NameSearchForm()
    context = {'form': form, 'searched': False}
    return render(request, 'xel/search.html', context)

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

@login_required
def handle_uploaded_file(excel_file_instance):
    df = pd.read_excel(excel_file_instance.file.path)
    if 'narration' in df.columns:
        for narration in df['narration'].dropna():
            NarrationEntry.objects.create(
                excel_file=excel_file_instance,
                narration=str(narration)
            )

@user_passes_test(lambda u: u.is_superuser)
def admin_xel(request):
    files = ExcelFile.objects.all()
    entries = NameEntry.objects.all()
    upload_form = ExcelUploadForm()
    if request.method == 'POST':
        upload_form = ExcelUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            upload_form.save()
            return redirect('admin')
    return render(request, 'xel/admin.html', {
        'files': files,
        'entries': entries,
        'upload_form': upload_form,
        'searched': False,
    })