import json
import hashlib
import hmac as hmac_module
import requests
import qrcode
import io
import base64
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from payments.models import Payment
from accounts.models import APIKey


def payment_page(request, payment_id, token):
    payment = get_object_or_404(Payment, id=payment_id)
    if payment.payment_token != token:
        raise Http404("Invalid payment link")

    upi_id = f"nexapay@upi"
    upi_url = f"upi://pay?pa={upi_id}&pn=NexaPay&am={payment.amount}&cu={payment.currency}"

    qr = qrcode.make(upi_url)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return render(request, 'payments/payment_page.html', {
        'payment': payment,
        'qr_code': qr_b64,
        'upi_id': upi_id,
    })


@csrf_exempt
def simulate_payment_success(request, payment_id, token):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    payment = get_object_or_404(Payment, id=payment_id)
    if payment.payment_token != token:
        return JsonResponse({'error': 'Invalid payment token'}, status=403)

    if payment.status == 'success':
        return JsonResponse({'error': 'Payment already completed'}, status=400)

    payment.status = 'success'
    payment.save()

    if payment.callback_url:
        try:
            api_key = APIKey.objects.get(business=payment.business)
            secret_key = api_key.decrypt_secret()
            payload = {
                'payment_id': str(payment.id),
                'amount': str(payment.amount),
                'status': 'success',
            }
            payload_str = json.dumps(payload, sort_keys=True)
            signature = hmac_module.new(
                secret_key.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            payload['signature'] = signature
            requests.post(payment.callback_url, json=payload, timeout=10)
        except Exception:
            pass

    return JsonResponse({
        'status': 'success',
        'payment_id': str(payment.id),
        'message': 'Payment completed successfully!'
    })
