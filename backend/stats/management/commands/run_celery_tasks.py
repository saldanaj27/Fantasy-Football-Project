from django.core.management.base import BaseCommand

from stats.tasks import (
    clear_all_cache,
    refresh_live_games,
    seed_all_data,
    seed_games,
    seed_players,
    seed_stats,
    weekly_data_refresh,
)

"""
============================================
Management Commands for Manual Execution
Used to manually trigger tasks (ex: 'python manage.py run_celery_task seed_games')
============================================
"""


class Command(BaseCommand):
    help = "Manually run Celery tasks"

    def add_arguments(self, parser):
        parser.add_argument(
            "task",
            type=str,
            help="Task to run: seed_players, seed_games, seed_stats, seed_all, weekly_refresh, live_games, clear_cache",
        )

    def handle(self, *args, **options):
        task_name = options["task"]

        tasks = {
            "seed_players": seed_players,
            "seed_games": seed_games,
            "seed_stats": seed_stats,
            "seed_all": seed_all_data,
            "weekly_refresh": weekly_data_refresh,
            "live_games": refresh_live_games,
            "clear_cache": clear_all_cache,
        }

        if task_name not in tasks:
            self.stdout.write(self.style.ERROR(f"Unknown task: {task_name}"))
            self.stdout.write(f'Available tasks: {", ".join(tasks.keys())}')
            return

        self.stdout.write(f"Running task: {task_name}...")

        # Run the task synchronously
        result = tasks[task_name].apply()

        self.stdout.write(self.style.SUCCESS(f"Task completed: {result.result}"))
