import sys
from django.apps import AppConfig

class SubscriptionBillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscription_billing'

    def ready(self):
        # Avoid running on migrate, shell, or test commands
        if 'runserver' not in sys.argv and 'celery' not in sys.argv:
            return

        from django_celery_beat.models import PeriodicTask, CrontabSchedule
        import json

        try:
            # Define crontab schedules for specific times
            generate_invoices_schedule, _ = CrontabSchedule.objects.get_or_create(
                minute='0',
                hour='10',   # 10 AM daily
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
            )

            mark_overdue_schedule, _ = CrontabSchedule.objects.get_or_create(
                minute='0',
                hour='0',    # 12 AM (midnight) daily
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
            )

            send_reminders_schedule, _ = CrontabSchedule.objects.get_or_create(
                minute='0',
                hour='21',   # 9 PM daily (21 in 24-hour format)
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
            )

            task_defs = [
                {
                    "name": "Generate Invoices Daily",
                    "task": "subscription_billing.tasks.generate_invoices",
                    "schedule": generate_invoices_schedule,
                },
                {
                    "name": "Mark Overdue Invoices",
                    "task": "subscription_billing.tasks.mark_overdue_invoices",
                    "schedule": mark_overdue_schedule,
                },
                {
                    "name": "Send Invoice Reminders",
                    "task": "subscription_billing.tasks.queue_reminders",
                    "schedule": send_reminders_schedule,
                }
            ]

            for task_def in task_defs:
                PeriodicTask.objects.update_or_create(
                    name=task_def["name"],
                    defaults={
                        "task": task_def["task"],
                        "crontab": task_def["schedule"],
                        "args": json.dumps([]),
                        "enabled": True,
                    }
                )

        except Exception as e:
            # Fail silently if DB not ready or on first migration
            print(f"[Schedule Auto-Create] Skipped: {e}")
