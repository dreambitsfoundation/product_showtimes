import datetime

from django.db import transaction
from imdb import Cinemagoer, Movie

from api.models import Showtime
from django.core.cache import cache


def get_unique_names(items: list):
    """
    This method simply extracts names from the
    items and only returns the unique ones.
    """
    unique_list = set({})
    for item in items:
        data = item.data.get("name", None)
        if data:
            unique_list.add(data)

    return list(unique_list)


def generate_movie_details(top_movies: list):
    ia = Cinemagoer()

    movie_details = list()
    for movie in top_movies:
        movie_info = ia.get_movie(movie.movieID)
        movie_data = movie_info.data
        details = dict({
            "title": movie_data.get("original title", ''),
            "movie_id": movie_data.get("imdbID", ''),
            "cover_url": movie_data.get('cover url', ''),
            "cast": get_unique_names(movie_data.get('cast', list())),
            "guest_appearance": get_unique_names(movie_data.get('thanks', list())),
            "directors": get_unique_names(movie_data.get('director', list())),
            "writers": get_unique_names(movie_data.get('writer', list())),
            "genres": movie_data.get('genres', list()),
            "rating": movie_data.get('rating', 0.0),
            "votes": movie_data.get('votes', 0),
            "plot": movie_data.get('plot'),
            "distributors": get_unique_names(movie_data.get("distributors", list())),
            "producers": get_unique_names(movie_data.get("producer", list())),
            "production_companies": get_unique_names(movie_data.get("production companies", list())),
            "year": movie_data.get('year', '')
        })

        movie_details.append(details)

    return movie_details


def create_db_record_for_new_showtimes(movie_detailed_objects, showtimes=None):
    """
    Creating Show timings for the movies.
    """
    if showtimes is None:
        showtimes = ["10:00", "14:00", "20:00"]

    db_instances_created = dict({})
    with transaction.atomic():
        """
        We are wrapping the code into the transaction because we want to make sure that the
        record is persisted only in-case all the show times were created and also the movie
        records are stored into the cache.
        """
        try:
            showtime_instances = list()
            # For each movie create 3 timings for today 10:00 AM, 2:00 PM, 8:00 PM
            for new_movie in movie_detailed_objects:
                for showtime in showtimes:
                    showtime_record, new_record = Showtime.objects.get_or_create(
                        movie=new_movie['title'],
                        movie_id=new_movie['movie_id'],
                        movie_release_year=new_movie['year'],
                        date=datetime.date.today(),
                        show_time=showtime
                    )
                    if new_record:
                        showtime_record.movie_details = new_movie
                        showtime_record.save()
                    showtime_instances.append(showtime_record)

                # Finally, add the respective instances with this movie ID
                db_instances_created[new_movie['movie_id']] = showtime_instances
        except:
            pass

        return db_instances_created


def get_top_shows_from_imdb(size: int = 25):
    """
    This methods loads the top 25 movies from the IMdb
    and stores their information into the cache, while
    creating show timings for today's screens
    """

    ia = Cinemagoer()

    # Extract all Box Office Movies and persist records in the provided size
    top_movies = ia.get_boxoffice_movies()[:size]

    # Now for each movie store the detailed information
    movie_detailed_objects = generate_movie_details(top_movies)

    # Create Show timing for movies
    show_timings = create_db_record_for_new_showtimes(movie_detailed_objects)

    # Finally, store the movie_detailed_objects into cache
    cache.set("top_movies", movie_detailed_objects, 86400)  # Expires in 1 day

    return movie_detailed_objects


def get_movies_from_cache():
    """
    Returns all the cached movies
    """
    result = cache.get("top_movies")
    if not result:
        print("Show records were not found on imdb")
        result = get_top_shows_from_imdb()

    return result
