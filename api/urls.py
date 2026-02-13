from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('create-payment/', views.create_payment, name='create_payment'),
]
