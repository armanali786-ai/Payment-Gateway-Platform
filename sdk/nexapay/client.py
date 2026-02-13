import requests


class Client:
    def __init__(self, public_key, base_url="https://localhost:5000"):
        self.public_key = public_key
        self.base_url = base_url.rstrip('/')

    def create_payment(self, amount, currency="INR", customer_name=None, customer_email=None, callback_url=None):
        url = f"{self.base_url}/api/create-payment/"
        headers = {
            'Authorization': f'Bearer {self.public_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'amount': amount,
            'currency': currency,
        }
        if customer_name:
            payload['customer_name'] = customer_name
        if customer_email:
            payload['customer_email'] = customer_email
        if callback_url:
            payload['callback_url'] = callback_url

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
