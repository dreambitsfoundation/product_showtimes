import datetime

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import AllowAny
from api.models import User, Showtime, Booking
from api.serializers import AccountSerializer, ShowTimeSerializer, BookingSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404

from service.views import get_movies_from_cache


class RegisterView(generics.CreateAPIView):
    """
    This view is used to create new Users
    """
    queryset = User.objects.all()
    serializer_class = AccountSerializer
    permission_classes = (AllowAny,)


class UserAuthentication(APIView):
    """
    This method is used for JWT authentication for existing users.
    """
    permission_classes = (IsAuthenticated,)


class GetAllTheLatestShows(APIView):
    """
    This view return all the movies up for show today
    """
    http_method_names = ['get']

    def get(self, request):
        queryset = get_movies_from_cache()
        return Response(queryset)


class ShowsForTheMovie(APIView):
    """
    This view returns the list of show times that are
    available for the movie ID
    """

    http_method_names = ['get']

    def get(self, request, movieID, format=None):
        queryset = Showtime.objects.filter(movie_id=movieID, date=datetime.date.today())
        serializer = ShowTimeSerializer(queryset, many=True)
        return Response(serializer.data)


class CreateShowBooking(APIView):
    """
    This Endpoint provides the service to book a show timing
    """
    permission_classes = (IsAuthenticated,)
    http_method_names = ['post']

    def get_showtime(self, id):
        try:
            return Showtime.objects.get(id=id)
        except:
            raise Http404

    def post(self, request, format=None):
        showtime_id = request.data.get('showtime_id')
        number_of_seats = request.data.get('seats', 1)

        # Get the showtime instance
        showtime = self.get_showtime(showtime_id)

        # Check the total number of available seats and total bookings
        total_booked_seats = Booking.objects.filter(show_timing=showtime, cancelled=False) \
            .aggregate(total_booked_seats=Coalesce(Sum('number_of_seats'), 0))
        print(total_booked_seats)
        available_seats_for_booking = showtime.max_seats - total_booked_seats.get('total_booked_seats', 0)

        print(f"Available Seats for Booking: {available_seats_for_booking}")

        if available_seats_for_booking >= int(number_of_seats):
            # Create booking instance
            booking = Booking(
                user=request.user,
                show_timing=showtime,
                movie_details=showtime.movie_details,
                number_of_seats=number_of_seats
            )
            booking.save()
            booking_serializer = BookingSerializer(booking)
            return Response(booking_serializer.data)
        else:
            return Response({'detail': 'Seats not available. Housefull!'})


class SeeAllBookings(APIView):
    """
    Returns all the bookings done by a User
    """
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def get(self, request):
        cancelled_item = request.query_params.get('cancelled', False)
        history = request.query_params.get('history', False)
        if not history:
            queryset = Booking.objects.filter(user=request.user, show_timing__date=datetime.date.today())
        else:
            queryset = Booking.objects.filter(user=request.user)
        if cancelled_item:
            queryset = queryset.filter(cancelled=cancelled_item)
        serializer = BookingSerializer(queryset, many=True)
        return Response(serializer.data)


class CancelBooking(APIView):
    """
    Cancel the seat booking.
    """
    permission_classes = (IsAuthenticated,)
    http_method_names = ['delete']

    def get_booking(self, booking_id):
        try:
            return Booking.objects.get(pk=booking_id)
        except Booking.DoesNotExist as e:
            raise Http404

    def delete(self, request, booking_id):
        booking_instance = self.get_booking(booking_id)

        if booking_instance.cancelled:
            return Response({'detail': 'This booking is already cancelled.'}, status=500)

        if booking_instance.user == request.user:
            booking_instance.cancelled = True
            booking_instance.cancelled_on = timezone.now()
            booking_instance.save()
            return Response({'message': 'Booking has been cancelled.'})
        else:
            return Response({
                'detail': 'Unauthorized! You can only cancel bookings made by you.'
            }, status=401)

