from datetime import date

from django.core.management.base import BaseCommand, CommandParser
from django.core.cache import cache

from api.models import Showtime


class Command(BaseCommand):
    help = "Clear the existing Movie Records from cache."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--delete_show_timings',
            type=bool,
            help="Whether to persist the created show timings for today or delete them too",
            default=False
        )

    def handle(self, *args, **params):
        # Deleting the cache
        print("Clearing Cache")
        cache.delete('top_movies')

        # If asked to delete the showtimes from db clear them too
        clear_showtime_records = params['delete_show_timings']

        if clear_showtime_records:
            print("Deleting Showtimes from DB")
            all_showtimes_from_today = Showtime.objects.filter(date=date.today())
            all_showtimes_from_today.delete()

        print("Process Completed!")
