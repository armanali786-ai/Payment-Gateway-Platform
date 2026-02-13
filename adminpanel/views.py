import csv
import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from payments.models import Payment
from accounts.models import BusinessProfile


def is_admin(user):
    return user.is_staff


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('adminpanel:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('adminpanel:dashboard')
        else:
            return render(request, 'adminpanel/login.html', {'error': 'Invalid admin credentials.'})

    return render(request, 'adminpanel/login.html')


def admin_logout(request):
    logout(request)
    return redirect('adminpanel:login')


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    businesses = BusinessProfile.objects.all()
    total_businesses = businesses.count()
    active_businesses = businesses.filter(is_active=True).count()

    all_payments = Payment.objects.all()
    successful = all_payments.filter(status='success')

    total_commission = successful.aggregate(s=Sum('commission_amount'))['s'] or 0
    total_revenue = successful.aggregate(s=Sum('amount'))['s'] or 0
    total_transactions = successful.count()

    now = timezone.now()
    six_months_ago = now - timedelta(days=180)
    monthly_data = (
        successful
        .filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(commission=Sum('commission_amount'), count=Count('id'))
        .order_by('month')
    )

    labels = []
    commission_chart = []
    for item in monthly_data:
        labels.append(item['month'].strftime('%b %Y'))
        commission_chart.append(float(item['commission']))

    business_data = (
        successful
        .values('business__business_name')
        .annotate(
            total=Sum('amount'),
            commission=Sum('commission_amount'),
            count=Count('id')
        )
        .order_by('-commission')
    )

    recent_transactions = all_payments.select_related('business').order_by('-created_at')[:50]

    context = {
        'total_businesses': total_businesses,
        'active_businesses': active_businesses,
        'total_commission': total_commission,
        'total_revenue': total_revenue,
        'total_transactions': total_transactions,
        'chart_labels': json.dumps(labels),
        'chart_commission': json.dumps(commission_chart),
        'business_data': business_data,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'adminpanel/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="nexapay_transactions.csv"'
    writer = csv.writer(response)
    writer.writerow(['Payment ID', 'Business', 'Amount', 'Commission', 'Net Amount', 'Status', 'Customer', 'Date'])
    payments = Payment.objects.select_related('business').order_by('-created_at')
    for p in payments:
        writer.writerow([
            str(p.id), p.business.business_name, p.amount, p.commission_amount,
            p.net_amount, p.status, p.customer_name or '', p.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    return response
