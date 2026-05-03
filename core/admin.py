from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User as DjangoAuthUser

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser


# Remove any pre-registered user models to avoid duplicate "Usuarios" in admin.
for user_model in (DjangoAuthUser, get_user_model()):
	try:
		admin.site.unregister(user_model)
	except NotRegistered:
		pass


@admin.register(CustomUser)
class CustomUserAdmin(DjangoUserAdmin):
	add_form = CustomUserCreationForm
	form = CustomUserChangeForm
	list_display = [
		"username",
		"email",
		"first_name",
		"last_name",
		"seller",
		"is_staff",
	]
	list_filter = ["seller", "is_staff", "is_active", "date_joined"]
	search_fields = ["username", "email", "first_name", "last_name"]
	add_fieldsets = (
		(
			None,
			{
				"classes": ("wide",),
				"fields": (
					"username",
					"email",
					"first_name",
					"last_name",
					"seller",
					"alojamientos",
					"actividades",
					"restaurantes",
					"planings",
					"password1",
					"password2",
				),
			},
		),
	)
	fieldsets = (
		(
			None,
			{"fields": ("username", "password")},
		),
		(
			"Información personal",
			{
				"fields": (
					"first_name",
					"last_name",
					"email",
					"seller",
					"alojamientos",
					"actividades",
					"restaurantes",
					"planings",
				),
			},
		),
		(
			"Permisos",
			{
				"fields": (
					"is_active",
					"is_staff",
					"is_superuser",
					"groups",
					"user_permissions",
				),
			},
		),
		(
			"Fechas importantes",
			{"fields": ("last_login", "date_joined")},
		),
	)
