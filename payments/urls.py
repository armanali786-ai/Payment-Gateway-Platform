from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('<uuid:payment_id>/<str:token>/', views.payment_page, name='payment_page'),
    path('<uuid:payment_id>/<str:token>/simulate-success/', views.simulate_payment_success, name='simulate_success'),
]
