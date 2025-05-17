from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from .models import Subscription, Invoice

logger = get_task_logger(__name__)

@shared_task
def generate_invoices():
    today = timezone.now().date()
    subscriptions = Subscription.objects.filter(
        status='active',
        start_date__lte=today,
        end_date__gte=today
    )

    for sub in subscriptions:
        last_invoice = sub.invoices.order_by('-issue_date').first()
        if last_invoice:
            if sub.plan.billing_interval == 'monthly':
                next_issue_date = last_invoice.issue_date + relativedelta(months=1)
            else:
                next_issue_date = last_invoice.issue_date + relativedelta(years=1)
            if next_issue_date != today:
                continue 

        due_date = today + timedelta(days=7)
        Invoice.objects.create(
            subscription=sub,
            amount=sub.plan.price,
            issue_date=today,
            due_date=due_date,
            status='pending'
        )

@shared_task
def mark_overdue_invoices():
    today = timezone.now().date()
    overdue_invoices = Invoice.objects.filter(status='pending', due_date__lt=today)
    overdue_invoices.update(status='overdue')

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 5})
def send_reminder_email(self, invoice_id):
    try:
        invoice = Invoice.objects.select_related('subscription__user', 'subscription__plan').get(pk=invoice_id)
    except ObjectDoesNotExist:
        logger.warning(f"Invoice {invoice_id} not found.")
        return

    today = timezone.now().date()
    user = invoice.subscription.user

    # Skip if already paid or cancelled
    if invoice.status == 'paid' or invoice.reminder_count >= 3:
        if invoice.reminder_count >= 3:
            invoice.subscription.status = 'cancelled'
            invoice.subscription.save()
            logger.info(f"Cancelled subscription for user {user.username} after 3 reminders.")
        return

    # Send only every 2 days
    if not invoice.last_reminder_sent or (today - invoice.last_reminder_sent).days >= 2:
        print(f"[MOCK EMAIL] Reminder to {user.email or user.username} for Invoice #{invoice.id} - Amount: {invoice.amount}")

        # Uncomment below to send real email:
        """
        send_mail(
            subject=f"Payment Reminder for Invoice #{invoice.id}",
            message=f"Dear {user.username}, your invoice of ${invoice.amount} is pending.",
            from_email="billing@yourapp.com",
            recipient_list=[user.email],
            fail_silently=False,
        )
        """

        invoice.reminder_count += 1
        invoice.last_reminder_sent = today
        invoice.save()
        logger.info(f"Reminder #{invoice.reminder_count} sent for invoice {invoice.id}")
    else:
        logger.info(f"Skipping reminder for invoice {invoice.id}; last sent recently.")

@shared_task
def queue_reminders():
    overdue_invoices = Invoice.objects.filter(status='overdue')
    for invoice in overdue_invoices:
        send_reminder_email.delay(invoice.id)
