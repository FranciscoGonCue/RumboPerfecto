from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Trip(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="trips",
    )
    title = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "start_date"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "La fecha fin no puede ser anterior a la fecha inicio."})
        if self.title is not None and not self.title.strip():
            raise ValidationError({"title": "El titulo no puede estar vacio."})

    def save(self, *args, **kwargs):
        if isinstance(self.title, str):
            self.title = self.title.strip()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.user_id})"


class Activity(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="activities")
    day = models.PositiveIntegerField()
    title = models.CharField(max_length=150)
    location = models.CharField(max_length=200)
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["day", "time", "created_at"]
        indexes = [
            models.Index(fields=["trip", "day"]),
            models.Index(fields=["trip", "time"]),
        ]

    def clean(self):
        errors = {}
        if self.day < 1:
            errors["day"] = "El dia debe ser mayor o igual que 1."
        if self.title is not None and not self.title.strip():
            errors["title"] = "El titulo no puede estar vacio."
        if self.location is not None and not self.location.strip():
            errors["location"] = "La ubicacion no puede estar vacia."

        if self.trip_id and self.day:
            trip_days = (self.trip.end_date - self.trip.start_date).days + 1
            if self.day > trip_days:
                errors["day"] = "El dia no puede ser mayor que la duracion del viaje."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if isinstance(self.title, str):
            self.title = self.title.strip()
        if isinstance(self.location, str):
            self.location = self.location.strip()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.trip_id}"
