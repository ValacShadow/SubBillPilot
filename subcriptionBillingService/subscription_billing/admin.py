from django.contrib import admin
from .models import Plan
from django_celery_beat.models import PeriodicTask, IntervalSchedule

admin.site.register(Plan)
