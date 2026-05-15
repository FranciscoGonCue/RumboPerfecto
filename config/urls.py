from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from core.views import (
    ChangePasswordView,
    LoginView,
    LogoutView,
    MeView,
    MisServiciosView,
    RegisterView,
    ServicioUpdateView,
    UpdateSellerView,
)
from marketdata.views import (
    CatalogoServicioDetailView,
    CatalogoServicioListView,
    ResenaServicioListCreateView,
)
from planning.views import (
    GeocodeAddressView,
    MisPlansView,
    MisReservasView,
    PlanDetailView,
    PlanItemDetailView,
    PlanItemsView,
    ReservaDetailView,
    ServicioReservaEstadoView,
    ServicioReservasView,
    TiposServicioView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view(), name="auth-register"),
    path("api/auth/login/", LoginView.as_view(), name="auth-login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("api/auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("api/auth/me/", MeView.as_view(), name="auth-me"),
    path("api/auth/change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
    path("api/auth/seller/", UpdateSellerView.as_view(), name="auth-seller"),
    path("api/auth/mis-servicios/", MisServiciosView.as_view(), name="auth-mis-servicios"),
    path(
        "api/auth/mis-servicios/<str:id_servicio>/",
        ServicioUpdateView.as_view(),
        name="auth-mis-servicios-update",
    ),
    path(
        "api/auth/mis-servicios/<str:id_servicio>/reservas/<int:pk>/",
        ServicioReservaEstadoView.as_view(),
        name="auth-servicio-reserva-estado",
    ),
    path(
        "api/auth/mis-servicios/<str:id_servicio>/reservas/",
        ServicioReservasView.as_view(),
        name="auth-servicio-reservas",
    ),
    path("api/auth/mis-reservas/", MisReservasView.as_view(), name="auth-mis-reservas"),
    path(
        "api/auth/mis-reservas/<int:pk>/",
        ReservaDetailView.as_view(),
        name="auth-reserva-detail",
    ),
    path("api/auth/mis-planes/", MisPlansView.as_view(), name="auth-mis-planes"),
    path("api/auth/mis-planes/<int:pk>/", PlanDetailView.as_view(), name="auth-plan-detail"),
    path("api/auth/mis-planes/<int:pk>/items/", PlanItemsView.as_view(), name="auth-plan-items"),
    path(
        "api/auth/mis-planes/<int:pk>/items/<int:item_pk>/",
        PlanItemDetailView.as_view(),
        name="auth-plan-item-detail",
    ),
    path("api/auth/geocode/", GeocodeAddressView.as_view(), name="auth-geocode"),
    path("api/tipos-servicio/", TiposServicioView.as_view(), name="tipos-servicio"),
    path("api/servicios/", CatalogoServicioListView.as_view(), name="servicios-list"),
    path(
        "api/servicios/<str:id_servicio>/resenas/",
        ResenaServicioListCreateView.as_view(),
        name="servicios-resenas",
    ),
    path(
        "api/servicios/<str:id_servicio>/",
        CatalogoServicioDetailView.as_view(),
        name="servicios-detail",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
