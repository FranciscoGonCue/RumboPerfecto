from django.contrib import admin
from .models import PlanViaje, ItemPlan, Reserva


class ItemPlanInline(admin.TabularInline):
    model = ItemPlan
    extra = 1
    fields = [
        'nombre_servicio', 'tipo',
        'fecha_hora_inicio', 'fecha_hora_fin',
        'precio_estimado', 'monto_total',
        'estado_pago', 'localizador_confirmacion',
    ]
    autocomplete_fields = ['tipo']
    show_change_link = True


@admin.register(PlanViaje)
class PlanViajeAdmin(admin.ModelAdmin):
    list_display = ['id_plan', 'nombre_plan', 'estado_plan', 'fecha_inicio', 'fecha_fin']
    list_filter = ['estado_plan']
    search_fields = ['nombre_plan']
    inlines = [ItemPlanInline]


@admin.register(ItemPlan)
class ItemPlanAdmin(admin.ModelAdmin):
    list_display = ['id_item', 'nombre_servicio', 'plan', 'tipo', 'fecha_hora_inicio', 'estado_pago', 'monto_total']
    list_filter = ['tipo', 'estado_pago']
    search_fields = ['nombre_servicio', 'localizador_confirmacion']
    autocomplete_fields = ['tipo', 'plan']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display  = ['id', 'servicio', 'usuario', 'fecha_inicio', 'fecha_fin', 'turno', 'personas', 'precio_total', 'estado', 'creado_en']
    list_filter   = ['estado', 'fecha_inicio']
    search_fields = ['usuario__email', 'usuario__name', 'servicio__nombre', 'servicio__id_servicio']
    autocomplete_fields = ['usuario', 'servicio']
    readonly_fields = ['creado_en']
    fieldsets = (
        ('Reserva', {
            'fields': ('usuario', 'servicio', 'estado')
        }),
        ('Fechas y turno', {
            'fields': ('fecha_inicio', 'fecha_fin', 'turno', 'personas')
        }),
        ('Precio y notas', {
            'fields': ('precio_total', 'notas', 'creado_en')
        }),
    )
