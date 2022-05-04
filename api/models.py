from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.db import models


class User(AbstractBaseUser, PermissionsMixin, models.Model):
    """
    This is a custom user model
    """
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    email = models.EmailField(unique=True, null=False)
    age = models.IntegerField(null=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class Showtime(models.Model):
    movie = models.CharField(max_length=100, null=False)
    movie_id = models.CharField(max_length=10, null=False)
    max_seats = models.IntegerField(default=10)
    movie_release_year = models.CharField(max_length=4, null=False)
    movie_details = models.JSONField(null=True)
    date = models.DateField(auto_now_add=True)
    show_time = models.CharField(max_length=10)


class Booking(models.Model):
    """
    This model holds all the user showtime booking records.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    show_timing = models.ForeignKey(Showtime, on_delete=models.SET_NULL, null=True)
    movie_details = models.JSONField(null=False)
    number_of_seats = models.IntegerField(default=1)
    cancelled = models.BooleanField(default=False)
    cancelled_on = models.DateTimeField(null=True)
