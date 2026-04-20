from django.contrib import admin

from .models import Activity, Trip


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "start_date", "end_date", "created_at")
    list_filter = ("start_date", "created_at")
    search_fields = ("title", "user__email", "user__username")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("id", "trip", "day", "title", "location", "time")
    list_filter = ("day", "time")
    search_fields = ("title", "location", "trip__title")
