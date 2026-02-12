from django.core.management.base import BaseCommand

from stats.tasks import seed_stats

"""
============================================
Quick Test Task
Test if Celery is working ('python manage.py test_celery.py')
============================================
"""


class Command(BaseCommand):
    help = "Test Celery connection"

    def handle(self, *args, **options):
        self.stdout.write("Testing Celery...")

        # Queue the task asynchronously
        result = seed_stats.delay()

        self.stdout.write(f"Task ID: {result.id}")
        self.stdout.write("Task queued! Check Celery worker logs.")
        self.stdout.write("You can check task status with:")
        self.stdout.write("  from celery.result import AsyncResult")
        self.stdout.write(f'  AsyncResult("{result.id}").status')
