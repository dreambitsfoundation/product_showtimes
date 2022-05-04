from datetime import date

from django.core.management.base import BaseCommand, CommandParser
from django.core.cache import cache

from api.models import Showtime
from service.views import get_top_shows_from_imdb


class Command(BaseCommand):
    help = "Load fresh movie records from IMDB"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--size',
            type=int,
            help="Number of records to be updated.",
            default=25
        )

    def handle(self, *args, **params):
        size = params['size']

        print(f"Parsing, total {size} movies from IMdb.")
        movies = get_top_shows_from_imdb(size=size)

        print(f"Total {len(movies)} Movies were updated into the system.")
        print("Process Completed!")
