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

### 1. Clone and Install

```bash
git clone <repo_url>
cd subscription_billing
python -m venv env
source env/bin/activate
pip install -r requirements.txt ```




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


## Run Migrations
 python manage.py migrate
