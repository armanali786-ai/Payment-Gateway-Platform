from django.shortcuts import render
from django.conf import settings
import os


def home(request):
    return render(request, 'landing/home.html')


def docs(request):
    base_url = f"https://{os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')}"
    return render(request, 'landing/docs.html', {'base_url': base_url})


def pricing(request):
    return render(request, 'landing/pricing.html')
