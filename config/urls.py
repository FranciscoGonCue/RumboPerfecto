from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from marketdata.views import CatalogoServicioListView
from tasks.views import TaskViewSet
from planning.views import MisPlansView, PlanDetailView, PlanItemDetailView, PlanItemsView, TiposServicioView
from travel.views import ActivityViewSet, ChangePasswordView, LoginView, LogoutView, MeView, MisServiciosView, RegisterView, TripViewSet, UpdateSellerView

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"trips", TripViewSet, basename="trip")
router.register(r"activities", ActivityViewSet, basename="activity")

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
    path("api/auth/mis-planes/", MisPlansView.as_view(), name="auth-mis-planes"),
    path("api/auth/mis-planes/<int:pk>/", PlanDetailView.as_view(), name="auth-plan-detail"),
    path("api/auth/mis-planes/<int:pk>/items/", PlanItemsView.as_view(), name="auth-plan-items"),
    path("api/auth/mis-planes/<int:pk>/items/<int:item_pk>/", PlanItemDetailView.as_view(), name="auth-plan-item-detail"),
    path("api/tipos-servicio/", TiposServicioView.as_view(), name="tipos-servicio"),
    path("api/", include(router.urls)),
    path("api/servicios/", CatalogoServicioListView.as_view(), name="servicios-list"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
