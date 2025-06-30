from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.views import generic
from .forms import NameSearchForm, ExcelUploadForm
from .models import NameEntry

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
def search_name(request):
    if request.method == 'POST':
        form = NameSearchForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name'].strip()
            last_name = form.cleaned_data['last_name'].strip()
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
            }
            return render(request, 'xel/search.html', context)
    else:
        form = NameSearchForm()
    context = {'form': form, 'searched': False}
    return render(request, 'xel/search.html', context)

@user_passes_test(lambda u: u.is_superuser)
def upload_xel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('search_name')  # Redirect to search page after upload
    else:
        form = ExcelUploadForm()
    return render(request, 'xel/upload.html', {'form': form})