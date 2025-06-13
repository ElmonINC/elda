from django.shortcuts import render

def index(request):
    return render(request, 'data_elda/index.html')

# Create your views here.
