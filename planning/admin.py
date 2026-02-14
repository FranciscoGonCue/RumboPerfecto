from django.contrib import admin
from .models import PlanViaje, ItemPlan, Reserva


@admin.register(PlanViaje)
class PlanViajeAdmin(admin.ModelAdmin):
    list_display = ['id_plan', 'nombre_plan', 'estado_plan', 'fecha_inicio', 'fecha_fin']
    list_filter = ['estado_plan']
    search_fields = ['nombre_plan']


@admin.register(ItemPlan)
class ItemPlanAdmin(admin.ModelAdmin):
    list_display = ['id_item', 'nombre_servicio', 'plan', 'tipo', 'fecha_hora_inicio']
    list_filter = ['tipo']
    search_fields = ['nombre_servicio', 'api_provider_id']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id_reserva', 'item', 'estado_pago', 'monto_total', 'fecha_transaccion']
    list_filter = ['estado_pago']
    search_fields = ['localizador_confirmacion']
