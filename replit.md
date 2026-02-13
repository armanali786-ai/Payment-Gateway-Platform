# NexaPay - SaaS Payment Gateway Platform

## Overview
NexaPay is a production-ready SaaS payment gateway platform built with Django. It functions similar to Razorpay, allowing businesses to register, generate API keys, and accept payments through a hosted payment page with simulated UPI/QR payments.

## Tech Stack
- **Backend**: Django 5.2, Django REST Framework, PostgreSQL
- **Frontend**: Django Templates, Tailwind CSS (CDN), Chart.js
- **Authentication**: Django session auth (business), JWT for API
- **Security**: Fernet encryption for API secrets, HMAC webhook signatures

## Project Structure
```
nexapay/
├── core/           # Django project settings & URLs
├── accounts/       # Business registration, login, API key management
├── payments/       # Payment model, hosted payment page, simulate success
├── dashboard/      # Business dashboard with charts & stats
├── api/            # REST API for payment creation
├── adminpanel/     # Admin dashboard, CSV export
├── landing/        # Landing page, docs, pricing
├── sdk/nexapay/    # Python SDK package
├── templates/      # All HTML templates
└── static/         # Static assets
```

## Key Features
- Multi-tenant isolation (all queries filtered by business)
- API key generation with encrypted secret keys
- Payment creation API with 1.5% commission calculation
- Hosted payment page with QR code and simulated UPI
- Business dashboard with Chart.js analytics
- Admin dashboard with all-business overview and CSV export
- HMAC webhook signature verification
- Python SDK for easy integration

## User Roles
- **Business User**: Register, generate API keys, create payments, view dashboard
- **Admin User**: Username: `admin`, Password: `admin123` (login at `/admin-panel/login/`)

## URLs
- `/` - Landing page
- `/accounts/register/` - Business registration
- `/accounts/login/` - Business login
- `/dashboard/` - Business dashboard
- `/admin-panel/login/` - Admin login
- `/admin-panel/` - Admin dashboard
- `/api/create-payment/` - Payment creation API
- `/payment/<uuid>/` - Hosted payment page
- `/docs/` - Developer documentation
- `/pricing/` - Pricing page

## API Usage
```
POST /api/create-payment/
Authorization: Bearer <PUBLIC_KEY>
Content-Type: application/json

{
  "amount": 1000,
  "currency": "INR",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "callback_url": "https://yoursite.com/webhook"
}
```

## Database
- PostgreSQL via DATABASE_URL environment variable
- Models: User, BusinessProfile, APIKey, Payment

## Running
```
python manage.py runserver 0.0.0.0:5000
```
