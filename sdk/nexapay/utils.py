import hmac
import hashlib
import json


def verify_webhook_signature(payload, received_signature, secret_key):
    signature_payload = {
        "payment_id": payload["payment_id"],
        "amount": payload["amount"],
        "status": payload["status"],
    }
    expected = hmac.new(
        secret_key.encode(),
        json.dumps(signature_payload, sort_keys=True).encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, received_signature)
