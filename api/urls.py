from django.urls import path

from rest_framework_simplejwt import views as jwt_views
from .views import (
    RegisterView,
    GetAllTheLatestShows,
    ShowsForTheMovie,
    CreateShowBooking,
    SeeAllBookings,
    CancelBooking
)

urlpatterns = [
    # Authentication Related endpoints
    path('account/register', RegisterView.as_view()),
    path('account/login', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Showtime catalog related endpoint
    path('shows/all', GetAllTheLatestShows.as_view()),
    path('shows/book', CreateShowBooking.as_view()),
    path('shows/<str:movieID>', ShowsForTheMovie.as_view()),

    # Bookings
    path('booking/all', SeeAllBookings.as_view()),
    path('booking/cancel/<str:booking_id>', CancelBooking.as_view()),
]