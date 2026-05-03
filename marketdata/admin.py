from django.contrib import admin
from .models import (
    TipoServicio,
    CatalogoServicio,
    DetalleAlojamiento,
    DetalleTransporte,
    DetalleRestauracion,
    DetalleActividad,
)


@admin.register(TipoServicio)
class TipoServicioAdmin(admin.ModelAdmin):
    list_display = ['id_tipo', 'nombre_tipo']
    search_fields = ['nombre_tipo']


@admin.register(CatalogoServicio)
class CatalogoServicioAdmin(admin.ModelAdmin):
    list_display = ['id_servicio', 'nombre', 'tipo', 'usuario', 'precio_base', 'disponible']
    list_filter = ['tipo', 'disponible']
    search_fields = ['id_servicio', 'nombre']
    autocomplete_fields = ['usuario']


@admin.register(DetalleAlojamiento)
class DetalleAlojamientoAdmin(admin.ModelAdmin):
    list_display = ['servicio', 'estrellas', 'hora_checkin', 'hora_checkout']


@admin.register(DetalleTransporte)
class DetalleTransporteAdmin(admin.ModelAdmin):
    list_display = ['servicio', 'ciudad_origen', 'ciudad_destino', 'compania']
    search_fields = ['ciudad_origen', 'ciudad_destino', 'compania', 'codigo_vuelo']


@admin.register(DetalleRestauracion)
class DetalleRestauracionAdmin(admin.ModelAdmin):
    list_display = ['servicio', 'tipo_cocina', 'es_vegano', 'precio_medio', 'requiere_reserva']
    list_filter = ['es_vegano', 'requiere_reserva']


@admin.register(DetalleActividad)
class DetalleActividadAdmin(admin.ModelAdmin):
    list_display = ['servicio', 'duracion_estimada', 'aforo_maximo', 'guia_incluido']
    list_filter = ['guia_incluido']
