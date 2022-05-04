from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIRequestFactory, APIClient
from api.models import User, Showtime
import os, django

from service.views import create_db_record_for_new_showtimes


class TestRegisterUserView(TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        last_user = User.objects.all().last()
        last_user.delete()

    def test_user_registration(self):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "product_showtimes.settings")
        django.setup()

        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@gmail.com",
            "password": "pass1234",
            "age": "30"
        }

        client = APIClient()
        response = client.post('/api/account/register', payload)

        new_users = User.objects.filter(email=payload['email'])

        self.assertTrue(new_users.count() == 1, "User was successfully created.")


class TestLoginView(TestCase):

    def setUp(self) -> None:
        user = User(
            first_name="Gourab",
            last_name="Saha",
            age=39,
            email="gourabsaha@outlook.in"
        )
        user.set_password("pass1234")
        user.save()

    def tearDown(self) -> None:
        user = User.objects.get(email="gourabsaha@outlook.in")
        user.delete()

    def test_login_request(self):
        payload = {
            "email": "gourabsaha@outlook.in",
            "password": "pass1234"
        }

        client = APIClient()
        response = client.post('/api/account/login', payload)

        self.assertIsNone(response.json().get('detail', None))


class TestGetAllTheLatestShowsView(TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_get_all_latest_shows(self):
        client = APIClient()
        response = client.get('/api/shows/all')

        self.assertIsInstance(response.json(), list)


class TestGetShowtimeForMovies(TestCase):

    def setUp(self) -> None:
        client = APIClient()
        response = client.get('/api/shows/all')

        movies = response.json()

        movie_db_instances = create_db_record_for_new_showtimes(movies)

    def tearDown(self) -> None:
        all_showtimes = Showtime.objects.all()
        all_showtimes.delete()

    def test_get_showtime_for_movies(self):
        client = APIClient()
        response = client.get('/api/shows/all')

        movies = response.json()
        movieId = movies[0]['movie_id']

        showtime_response = client.get(f'/api/shows/{movieId}')
        self.assertTrue(len(showtime_response.json()) >= 3, "Minimum 3 show times are available.")


class TestShowtimeBookingAndCancellation(TestCase):

    def setUp(self) -> None:
        client = APIClient()
        response = client.get('/api/shows/all')

        movies = response.json()

        movie_db_instances = create_db_record_for_new_showtimes(movies)

        user = User(
            first_name="Gourab",
            last_name="Saha",
            age=39,
            email="gourabsaha@outlook.in"
        )
        user.set_password("pass1234")
        user.save()

        payload = {
            'email': user.email,
            'password': 'pass1234'
        }

        client = APIClient()
        response = client.post('/api/account/login', payload)

        self.token = response.json()['access']

    def tearDown(self) -> None:
        # Delete all showtimes
        all_showtimes = Showtime.objects.all()
        all_showtimes.delete()

        # Delete all users
        users = User.objects.all()
        users.delete()

    def test_booking_and_cancellation_of_showtimes(self):
        client = APIClient()
        response = client.get('/api/shows/all')

        movies = response.json()
        movieId = movies[0]['movie_id']

        showtime_response = client.get(f'/api/shows/{movieId}')

        self.assertTrue(len(showtime_response.json()) >= 3, "Minimum 3 show times are available.")

        showtime_data = showtime_response.json()

        if len(showtime_data) > 0:
            show_id = showtime_response.json()[0]['id']
            max_seats = showtime_response.json()[0]['max_seats']

            # Login into client
            client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

            # Purchase all tickets at once
            payload = {
                "showtime_id": show_id,
                "seats": max_seats
            }
            response = client.post('/api/shows/book', payload)

            print(response.json())
            self.assertTrue(response.status_code, 200)
            self.assertTrue(response.json().get('detail', None) is None)

            # Persist the Booking ID to test cancellation
            self.booking_id = response.json()['id']

            # Trying to buy another ticket
            payload = {
                "showtime_id": show_id,
                "seats": 1
            }
            response = client.post('/api/shows/book', payload)

            self.assertTrue(response.status_code, 200)
            self.assertTrue(response.json().get('detail', None) is not None)

            # Cancel the first Booking
            response = client.delete(f'/api/booking/cancel/{self.booking_id}')
            self.assertTrue(response.status_code, 200)
            self.assertTrue(response.json().get('detail', None) is None)

            # Try booking for a single seat
            payload = {
                "showtime_id": show_id,
                "seats": 1
            }
            response = client.post('/api/shows/book', payload)

            self.assertTrue(response.status_code, 200)
            self.assertTrue(response.json().get('detail', None) is None)
