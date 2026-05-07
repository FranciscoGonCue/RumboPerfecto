from django import forms
from django.contrib import admin
from .models import (
    TipoServicio,
    CatalogoServicio,
    DetalleAlojamiento,
    DetalleTransporte,
    DetalleRestauracion,
    DetalleActividad,
)
from .widgets import AvailabilityCalendarWidget


class DetalleAlojamientoForm(forms.ModelForm):
    class Meta:
        model = DetalleAlojamiento
        fields = '__all__'
        widgets = {
            'fechas_no_disponibles': AvailabilityCalendarWidget(),
        }


class DetalleActividadForm(forms.ModelForm):
    class Meta:
        model = DetalleActividad
        fields = '__all__'
        widgets = {
            'fechas_no_disponibles': AvailabilityCalendarWidget(),
        }


class DetalleRestauracionForm(forms.ModelForm):
    class Meta:
        model = DetalleRestauracion
        fields = '__all__'
        widgets = {
            'fechas_no_disponibles': AvailabilityCalendarWidget(),
        }


@admin.register(TipoServicio)
class TipoServicioAdmin(admin.ModelAdmin):
    list_display = ['id_tipo', 'nombre_tipo']
    search_fields = ['nombre_tipo']


class DetalleAlojamientoInline(admin.StackedInline):
    model = DetalleAlojamiento
    form = DetalleAlojamientoForm
    can_delete = False
    verbose_name = 'Detalle alojamiento'
    verbose_name_plural = 'Detalle alojamiento'
    fieldsets = (
        (None, {
            'fields': ('estrellas', 'hora_checkin', 'hora_checkout', 'amenidades')
        }),
        ('Disponibilidad', {
            'fields': ('fecha_disponible_desde', 'fecha_disponible_hasta', 'fechas_no_disponibles'),
            'description': 'Haz clic en los días del calendario para marcarlos como no disponibles.',
        }),
    )


class DetalleTransporteInline(admin.StackedInline):
    model = DetalleTransporte
    can_delete = False
    verbose_name = 'Detalle transporte'
    verbose_name_plural = 'Detalle transporte'


class DetalleRestauracionInline(admin.StackedInline):
    model = DetalleRestauracion
    form = DetalleRestauracionForm
    can_delete = False
    verbose_name = 'Detalle restauración'
    verbose_name_plural = 'Detalle restauración'
    fieldsets = (
        (None, {
            'fields': ('tipo_cocina', 'rango_precios', 'precio_medio', 'ubicacion_texto',
                       'es_vegano', 'requiere_reserva', 'abierto_ahora', 'especialidades', 'horario')
        }),
        ('Disponibilidad', {
            'fields': (
                'fecha_disponible_desde', 'fecha_disponible_hasta',
                'fechas_no_disponibles', 'turnos_disponibles', 'turnos_ocupados',
            ),
            'description': (
                'Haz clic en los días del calendario para bloquearlos (día entero).<br>'
                'turnos_disponibles: plantilla, ej: ["13:00","14:30","20:00"]<br>'
                'turnos_ocupados: JSON {"YYYY-MM-DD": ["13:00"]} — lo rellena el sistema al reservar.'
            ),
        }),
    )


class DetalleActividadInline(admin.StackedInline):
    model = DetalleActividad
    form = DetalleActividadForm
    can_delete = False
    verbose_name = 'Detalle actividad'
    verbose_name_plural = 'Detalle actividad'
    fieldsets = (
        (None, {
            'fields': ('dificultad', 'duracion_estimada', 'duracion_texto', 'aforo_maximo',
                       'ubicacion_texto', 'horario_apertura', 'guia_incluido', 'incluye', 'requisitos')
        }),
        ('Disponibilidad', {
            'fields': (
                'fecha_disponible_desde', 'fecha_disponible_hasta',
                'fechas_no_disponibles', 'turnos_disponibles', 'turnos_ocupados',
            ),
            'description': (
                'Haz clic en los días del calendario para bloquearlos (día entero).<br>'
                'turnos_disponibles: plantilla, ej: ["09:00","12:00","17:30"]<br>'
                'turnos_ocupados: JSON {"YYYY-MM-DD": ["09:00"]} — lo rellena el sistema al reservar.'
            ),
        }),
    )


_TIPO_INLINE_MAP = {
    'alojamiento': DetalleAlojamientoInline,
    'transporte':  DetalleTransporteInline,
    'restauracion': DetalleRestauracionInline,
    'restaurante':  DetalleRestauracionInline,
    'actividad':    DetalleActividadInline,
}


@admin.register(CatalogoServicio)
class CatalogoServicioAdmin(admin.ModelAdmin):
    list_display = ['id_servicio', 'nombre', 'tipo', 'ciudad', 'precio_base', 'valoracion', 'destacado', 'disponible']
    list_filter = ['tipo', 'disponible', 'destacado', 'pais']
    search_fields = ['id_servicio', 'nombre', 'ciudad']
    autocomplete_fields = ['usuario']

    def get_inlines(self, request, obj=None):
        if obj is None or obj.tipo is None:
            # Servicio nuevo: mostrar todos para que el usuario elija
            return [
                DetalleAlojamientoInline,
                DetalleTransporteInline,
                DetalleRestauracionInline,
                DetalleActividadInline,
            ]
        nombre_tipo = (obj.tipo.nombre_tipo or '').lower()
        for key, inline_cls in _TIPO_INLINE_MAP.items():
            if key in nombre_tipo:
                return [inline_cls]
        return []

    fieldsets = (
        ('Información básica', {
            'fields': ('id_servicio', 'tipo', 'usuario', 'nombre', 'descripcion', 'imagen_url', 'disponible', 'destacado')
        }),
        ('Ubicación', {
            'fields': ('ciudad', 'pais', 'direccion', 'ubicacion_lat', 'ubicacion_lon')
        }),
        ('Precio y valoración', {
            'fields': ('precio_base', 'moneda', 'valoracion', 'num_resenas')
        }),
        ('Etiquetas', {
            'fields': ('etiquetas',),
            'description': 'Lista JSON de etiquetas, ej: ["playa", "familiar"]'
        }),
    )


@admin.register(DetalleAlojamiento)
class DetalleAlojamientoAdmin(admin.ModelAdmin):
    form = DetalleAlojamientoForm
    list_display = ['servicio', 'estrellas', 'hora_checkin', 'hora_checkout', 'fecha_disponible_desde', 'fecha_disponible_hasta']
    fieldsets = (
        ('Check-in / Check-out', {
            'fields': ('servicio', 'estrellas', 'hora_checkin', 'hora_checkout')
        }),
        ('Disponibilidad', {
            'fields': ('fecha_disponible_desde', 'fecha_disponible_hasta', 'fechas_no_disponibles'),
            'description': (
                'Define el rango disponible con los dos campos de fecha y, a continuación, '
                'haz clic en los días del calendario para marcarlos como no disponibles (rojo).'
            )
        }),
        ('Amenities', {
            'fields': ('amenidades',),
            'description': 'amenidades: lista JSON, ej: ["wifi","pool","spa","breakfast"] — usar este campo para el frontend'
        }),
    )


@admin.register(DetalleTransporte)
class DetalleTransporteAdmin(admin.ModelAdmin):
    list_display = ['servicio', 'ciudad_origen', 'ciudad_destino', 'compania', 'duracion_minutos', 'asientos_disponibles']
    search_fields = ['ciudad_origen', 'ciudad_destino', 'compania', 'codigo_vuelo']
    fieldsets = (
        ('Ruta', {
            'fields': ('servicio', 'ciudad_origen', 'ciudad_destino', 'compania', 'codigo_vuelo', 'duracion_minutos')
        }),
        ('Disponibilidad', {
            'fields': ('asientos_disponibles', 'horarios_salida'),
            'description': 'horarios_salida: lista JSON, ej: ["08:10","12:40","19:05"]'
        }),
        ('Clases y comodidades', {
            'fields': ('clases', 'comodidades'),
            'description': (
                'clases: lista JSON, ej: [{"nombre":"Básica","recargo":0},{"nombre":"Confort","recargo":25}]<br>'
                'comodidades: lista JSON, ej: ["Wi-Fi","Equipaje mano","Snack"]'
            )
        }),
    )


@admin.register(DetalleRestauracion)
class DetalleRestauracionAdmin(admin.ModelAdmin):
    form = DetalleRestauracionForm
    list_display = ['servicio', 'tipo_cocina', 'rango_precios', 'precio_medio', 'es_vegano', 'requiere_reserva', 'abierto_ahora']
    list_filter = ['es_vegano', 'requiere_reserva', 'abierto_ahora', 'rango_precios']
    fieldsets = (
        ('Info general', {
            'fields': ('servicio', 'tipo_cocina', 'rango_precios', 'precio_medio', 'ubicacion_texto')
        }),
        ('Opciones', {
            'fields': ('es_vegano', 'requiere_reserva', 'abierto_ahora')
        }),
        ('Carta y horario', {
            'fields': ('especialidades', 'horario'),
            'description': (
                'especialidades: lista JSON, ej: ["Arroz meloso","Tarta de queso"]<br>'
                'horario: objeto JSON, ej: {"Lun":"13:00-16:00 · 20:00-23:00","Dom":"Cerrado"}'
            )
        }),
        ('Disponibilidad', {
            'fields': (
                'fecha_disponible_desde', 'fecha_disponible_hasta',
                'fechas_no_disponibles', 'turnos_disponibles', 'turnos_ocupados',
            ),
            'description': (
                'Define el rango disponible y haz clic en el calendario para bloquear días enteros.<br>'
                'turnos_disponibles: plantilla, ej: ["13:00","14:30"]<br>'
                'turnos_ocupados: JSON por fecha (horas ya reservadas), lo rellena el sistema.'
            )
        }),
    )


@admin.register(DetalleActividad)
class DetalleActividadAdmin(admin.ModelAdmin):
    form = DetalleActividadForm
    list_display = ['servicio', 'dificultad', 'duracion_texto', 'aforo_maximo', 'guia_incluido', 'ubicacion_texto']
    list_filter = ['guia_incluido', 'dificultad']
    fieldsets = (
        ('Info general', {
            'fields': ('servicio', 'dificultad', 'duracion_estimada', 'duracion_texto', 'aforo_maximo', 'ubicacion_texto', 'horario_apertura', 'guia_incluido')
        }),
        ('Contenido', {
            'fields': ('incluye', 'requisitos'),
            'description': (
                'incluye: lista JSON, ej: ["Guía local","Agua","Seguro"]<br>'
                'requisitos: lista JSON, ej: ["Calzado cómodo","Agua 1L"]'
            )
        }),
        ('Disponibilidad', {
            'fields': (
                'fecha_disponible_desde', 'fecha_disponible_hasta',
                'fechas_no_disponibles', 'turnos_disponibles', 'turnos_ocupados',
            ),
            'description': (
                'Define el rango disponible y haz clic en el calendario para bloquear días enteros.<br>'
                'turnos_disponibles: plantilla, ej: ["09:00","12:00"]<br>'
                'turnos_ocupados: JSON por fecha (horas ya reservadas), lo rellena el sistema.'
            )
        }),
    )
