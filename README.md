# 🧾 Subscription Billing Backend

A Django + DRF-based backend to manage user subscriptions, plans, automated invoicing, and reminders using Celery.

---

## 🚀 Features

- 🔐 Token-based authentication
- 📦 Dynamic plan creation (monthly, yearly)
- 📥 User subscriptions (with historical tracking)
- 🧾 Invoice generation via Celery
- ⏰ Automatic overdue tracking and reminders
- ⚠️ Subscription cancellation after 3 missed reminders
- 📬 Console-based reminder system (mock email)

---

## 🛠️ Technologies

- **Django** 4.x
- **Django REST Framework**
- **Celery** with **Redis**
- **django-celery-beat**
- **PostgreSQL** 
---


---

## ⚙️ Setup Instructions

### Clone and Install

```git clone https://github.com/ValacShadow/SubBillPilot.git```
```python -m venv env```
```source env/bin/activate```
```pip install -r requirements.txt```
### Run Migrations
 ```python manage.py migrate ```
### Start Redis
```docker run -d -p 6379:6379 --name redis-billing-service redis```
### Run Celery
```celery -A subcriptionBillingService worker --loglevel=info```
```celery -A subcriptionBillingService beat --loglevel=info```
### Start Server
```python manage.py runserver```

| URL                       | Method | Description                 |
| ------------------------- | ------ | --------------------------- |
| `/api/signup/`            | POST   | Register a new user         |
| `/api/login/`             | POST   | Token-based login           |
| `/api/plans/`             | GET    | View available plans        |
| `/api/subscribe/`         | POST   | Subscribe to a plan         |
| `/api/unsubscribe/`       | POST   | Cancel current subscription |
| `/api/invoices/`          | GET    | List user invoices          |
| `/api/invoices/<id>/`     | GET    | View invoice detail         |
| `/api/invoices/<id>/pay/` | POST   | Mock pay an invoice         |

# Scheduled Celery Tasks

| Task Name              | Task Path                              | Schedule           | Description                     |
|------------------------|--------------------------------------|--------------------|---------------------------------|
| Generate Invoices Daily | `subscription_billing.tasks.generate_invoices` | Every day at 10:00 AM  | Generates invoices for active subscriptions daily at 10 AM. |
| Mark Overdue Invoices  | `subscription_billing.tasks.mark_overdue_invoices` | Every day at 12:00 AM (midnight) | Marks pending invoices as overdue at midnight daily. |
| Send Invoice Reminders  | `subscription_billing.tasks.queue_reminders` | Every day at 9:00 PM    | Sends reminder emails for overdue invoices daily at 9 PM. |

---

**Note:** All times are in server timezone (usually UTC unless configured otherwise).

### Run task manually
```python manage.py shell```
```from subscription_billing.tasks import generate_invoices```
```generate_invoices.delay()```








