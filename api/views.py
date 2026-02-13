import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from accounts.models import APIKey
from payments.models import Payment


def get_base_url(request):
    scheme = 'https' if request.is_secure() or request.META.get('HTTP_X_FORWARDED_PROTO') == 'https' else 'http'
    host = request.META.get('HTTP_HOST', 'localhost')
    return f"{scheme}://{host}"


@csrf_exempt
def create_payment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return JsonResponse({'error': 'Missing or invalid Authorization header'}, status=401)

    public_key = auth_header.replace('Bearer ', '').strip()

    try:
        api_key = APIKey.objects.select_related('business').get(public_key=public_key)
    except APIKey.DoesNotExist:
        return JsonResponse({'error': 'Invalid API key'}, status=401)

    if not api_key.business.is_active:
        return JsonResponse({'error': 'Business account is inactive'}, status=403)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    amount = data.get('amount')
    if not amount:
        return JsonResponse({'error': 'Amount is required'}, status=400)

    try:
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError
    except (ValueError, Exception):
        return JsonResponse({'error': 'Invalid amount'}, status=400)

    currency = data.get('currency', 'INR')
    customer_name = data.get('customer_name', '')
    customer_email = data.get('customer_email', '')
    callback_url = data.get('callback_url', '')

    commission, net_amount = Payment.calculate_commission(amount)

    payment = Payment.objects.create(
        business=api_key.business,
        amount=amount,
        currency=currency,
        commission_amount=commission,
        net_amount=net_amount,
        customer_name=customer_name,
        customer_email=customer_email,
        callback_url=callback_url,
        status='created',
    )

    base_url = get_base_url(request)
    payment_url = f"{base_url}/payment/{payment.id}/{payment.payment_token}/"

    return JsonResponse({
        'success': True,
        'payment_id': str(payment.id),
        'payment_url': payment_url,
        'amount': str(payment.amount),
        'currency': payment.currency,
        'status': payment.status,
    }, status=201)
