from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Activity, Trip

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["email", "password", "name"]

    def validate_email(self, value):
        email = value.strip().lower()
        if not email:
            raise serializers.ValidationError("El email es obligatorio.")
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return email

    def create(self, validated_data):
        name = validated_data.pop("name", "").strip()
        email = validated_data["email"]
        username = email
        first_name = ""
        last_name = ""

        if name:
            parts = name.split(" ", 1)
            first_name = parts[0]
            if len(parts) > 1:
                last_name = parts[1]

        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data["password"],
            first_name=first_name,
            last_name=last_name,
        )
        return user


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ["id", "trip", "day", "title", "location", "time", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at", "trip"]


class TripSerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = ["id", "title", "start_date", "end_date", "activities", "created_at", "updated_at"]
        read_only_fields = ["id", "activities", "created_at", "updated_at"]


class TripWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ["id", "title", "start_date", "end_date", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ActivityWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ["id", "trip", "day", "title", "location", "time", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at", "trip"]
