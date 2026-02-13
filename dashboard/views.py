import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from payments.models import Payment
from accounts.models import APIKey


@login_required
def dashboard_home(request):
    profile = request.user.businessprofile
    has_api_key = hasattr(profile, 'api_key')

    secret_key_display = request.session.pop('show_secret_key', None)

    api_key = None
    if has_api_key:
        api_key = profile.api_key

    payments = Payment.objects.filter(business=profile)
    successful_payments = payments.filter(status='success')

    total_revenue = successful_payments.aggregate(s=Sum('amount'))['s'] or 0
    total_commission = successful_payments.aggregate(s=Sum('commission_amount'))['s'] or 0
    net_settlement = successful_payments.aggregate(s=Sum('net_amount'))['s'] or 0
    total_orders = successful_payments.count()

    now = timezone.now()
    six_months_ago = now - timedelta(days=180)
    monthly_data = (
        successful_payments
        .filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(
            revenue=Sum('amount'),
            commission=Sum('commission_amount'),
            count=Count('id')
        )
        .order_by('month')
    )

    labels = []
    revenue_data = []
    commission_data = []
    growth_data = []
    for item in monthly_data:
        labels.append(item['month'].strftime('%b %Y'))
        revenue_data.append(float(item['revenue']))
        commission_data.append(float(item['commission']))
        growth_data.append(item['count'])

    recent_payments = payments.order_by('-created_at')[:10]

    context = {
        'profile': profile,
        'has_api_key': has_api_key,
        'api_key': api_key,
        'secret_key_display': secret_key_display,
        'total_revenue': total_revenue,
        'total_commission': total_commission,
        'net_settlement': net_settlement,
        'total_orders': total_orders,
        'recent_payments': recent_payments,
        'chart_labels': json.dumps(labels),
        'chart_revenue': json.dumps(revenue_data),
        'chart_commission': json.dumps(commission_data),
        'chart_growth': json.dumps(growth_data),
    }
    return render(request, 'dashboard/home.html', context)
