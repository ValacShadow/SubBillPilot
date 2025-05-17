# subscription_billing/apps.py

from django.apps import AppConfig
import sys


class SubscriptionBillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscription_billing'

    def ready(self):
        # Avoid running on migrate, shell, or test commands
        if 'runserver' not in sys.argv and 'celery' not in sys.argv:
            return

        from django_celery_beat.models import PeriodicTask, IntervalSchedule
        import json

        try:
            # Create a 1-day interval schedule
            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=1,
                period=IntervalSchedule.DAYS
            )

            task_defs = [
                {
                    "name": "Generate Invoices Daily",
                    "task": "subscription_billing.tasks.generate_invoices",
                },
                {
                    "name": "Mark Overdue Invoices",
                    "task": "subscription_billing.tasks.mark_overdue_invoices",
                },
                {
                    "name": "Send Invoice Reminders",
                    "task": "subscription_billing.tasks.queue_reminders",
                }
            ]

            for task_def in task_defs:
                PeriodicTask.objects.get_or_create(
                    name=task_def["name"],
                    task=task_def["task"],
                    interval=schedule,
                    defaults={"args": json.dumps([])}
                )

        except Exception as e:
            # Fail silently if DB not ready or on first migration
            print(f"[Schedule Auto-Create] Skipped: {e}")
