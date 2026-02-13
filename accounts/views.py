from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import BusinessProfile, APIKey


def business_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        business_name = request.POST.get('business_name', '').strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        BusinessProfile.objects.create(
            user=user,
            business_name=business_name,
            business_email=email,
        )
        login(request, user)
        messages.success(request, 'Registration successful! Generate your API Key to start accepting payments.')
        return redirect('dashboard:home')

    return render(request, 'accounts/register.html')


def business_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and hasattr(user, 'businessprofile'):
            login(request, user)
            return redirect('dashboard:home')
        elif user and user.is_staff:
            messages.error(request, 'Please use the admin login page.')
        else:
            messages.error(request, 'Invalid credentials.')

    return render(request, 'accounts/login.html')


def business_logout(request):
    logout(request)
    return redirect('landing:home')


@login_required
def generate_api_key(request):
    if request.method != 'POST':
        return redirect('dashboard:home')

    profile = request.user.businessprofile
    public_key, secret_key = APIKey.generate_keys()

    api_key, created = APIKey.objects.get_or_create(business=profile)
    api_key.public_key = public_key
    api_key.encrypt_secret(secret_key)
    api_key.save()

    request.session['show_secret_key'] = secret_key
    messages.success(request, 'API Key generated successfully! Save your Secret Key — it won\'t be shown again.')
    return redirect('dashboard:home')
