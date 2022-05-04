from rest_framework import serializers
from api.models import User as UserModel, Showtime, Booking
from rest_framework.validators import UniqueValidator


class AccountSerializer(serializers.ModelSerializer):
    """
    This serializer has relation with the api.User model
    """
    # first_name = serializers.CharField(max_length=50, required=True)
    # last_name = serializers.CharField(max_length=50, required=True)
    # email = serializers.EmailField(
    #     required=True,
    #     validators=UniqueValidator(queryset=UserModel.objects.all())
    # )
    # age = serializers.IntegerField(required=True)
    # password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name', 'email', 'age', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def get_queryset(self):
        return UserModel.objects.all()

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = UserModel(**validated_data)
        user.set_password(password)
        user.save()

        return user


class ShowTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Showtime
        fields = ('id', 'movie', 'movie_id', 'max_seats', 'movie_release_year', 'date', 'show_time')


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
