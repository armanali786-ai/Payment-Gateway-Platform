from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('', views.admin_dashboard, name='dashboard'),
    path('export-csv/', views.export_csv, name='export_csv'),
]
