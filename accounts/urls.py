from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.business_register, name='register'),
    path('login/', views.business_login, name='login'),
    path('logout/', views.business_logout, name='logout'),
    path('generate-api-key/', views.generate_api_key, name='generate_api_key'),
]
