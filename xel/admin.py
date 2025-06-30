# xel/admin.py
from django.contrib import admin
from .models import ExcelFile, NameEntry

admin.site.register(NameEntry)  # Optional for debugging