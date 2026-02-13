import secrets
import hashlib
import hmac as hmac_module
from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.conf import settings
import base64


def get_fernet():
    key = settings.NEXAPAY_ENCRYPTION_KEY.encode()
    key = base64.urlsafe_b64encode(hashlib.sha256(key).digest())
    return Fernet(key)


class BusinessProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    business_email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.business_name


class APIKey(models.Model):
    business = models.OneToOneField(BusinessProfile, on_delete=models.CASCADE, related_name='api_key')
    public_key = models.CharField(max_length=64, unique=True, db_index=True)
    encrypted_secret_key = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"API Key for {self.business.business_name}"

    @staticmethod
    def generate_keys():
        public_key = 'npk_' + secrets.token_hex(14)
        secret_key = 'nsk_' + secrets.token_hex(30)
        return public_key, secret_key

    def encrypt_secret(self, secret_key):
        f = get_fernet()
        self.encrypted_secret_key = f.encrypt(secret_key.encode()).decode()

    def decrypt_secret(self):
        f = get_fernet()
        return f.decrypt(self.encrypted_secret_key.encode()).decode()

    @staticmethod
    def generate_hmac_signature(secret_key, payload_str):
        return hmac_module.new(
            secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
