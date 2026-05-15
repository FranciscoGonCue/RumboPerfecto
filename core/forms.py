import logging

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.db import DatabaseError
from django.utils.safestring import mark_safe

from .models import CustomUser

logger = logging.getLogger(__name__)


def _plan_choices() -> list[tuple[str, str]]:
    try:
        from planning.models import PlanViaje

        qs = PlanViaje.objects.select_related("usuario").order_by("nombre_plan")
        return [(str(p.id_plan), f"{p.nombre_plan or f'Plan {p.id_plan}'}") for p in qs]
    except ImportError:
        return []
    except DatabaseError:
        logger.warning("core.forms: tabla planning no disponible al cargar plan_choices", exc_info=True)
        return []
    except Exception:
        logger.warning("core.forms: error inesperado en plan_choices", exc_info=True)
        return []


def _choices(tipo_nombre: str) -> list[tuple[str, str]]:
    try:
        from marketdata.models import CatalogoServicio

        qs = (
            CatalogoServicio.objects.filter(tipo__nombre_tipo=tipo_nombre, disponible=True).order_by("nombre")
        )
        return [(s.id_servicio, s.nombre or s.id_servicio) for s in qs]
    except ImportError:
        return []
    except DatabaseError:
        logger.warning("core.forms: BD no disponible al cargar choices de servicios (%s)", tipo_nombre, exc_info=True)
        return []
    except Exception:
        logger.warning("core.forms: error inesperado en choices (%s)", tipo_nombre, exc_info=True)
        return []


class TomSelectMultiple(forms.SelectMultiple):

    class Media:
        css = {'all': ('https://cdn.jsdelivr.net/npm/tom-select@2.3.1/dist/css/tom-select.bootstrap5.min.css',)}
        js = ('https://cdn.jsdelivr.net/npm/tom-select@2.3.1/dist/js/tom-select.complete.min.js',)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs['id'] = attrs.get('id', f'id_{name}')
        html = super().render(name, value, attrs, renderer)
        uid = attrs['id']
        script = (
            f'<script>'
            f'(function(){{'
            f'  function init(){{'
            f'    var el = document.getElementById("{uid}");'
            f'    if(!el||el._tomSelect) return;'
            f'    new TomSelect(el,{{plugins:["remove_button"],'
            f'    placeholder:"Buscar...",maxOptions:200}});'
            f'  }}'
            f'  if(document.readyState==="loading"){{document.addEventListener("DOMContentLoaded",init);}}'
            f'  else{{init();}}'
            f'}})();'
            f'</script>'
        )
        return mark_safe(html + script)


class ServiceMultipleChoiceField(forms.MultipleChoiceField):

    def to_python(self, value):
        return list(value) if value else []

    def validate(self, value):
        if not isinstance(value, list):
            raise forms.ValidationError("Valor inválido.")


class _ServiceFormMixin:

    def _init_service_fields(self):
        self.fields['alojamientos'].choices = _choices('Alojamiento')
        self.fields['actividades'].choices = _choices('Actividad')
        self.fields['restaurantes'].choices = _choices('Restauración')
        self.fields['planings'].choices = _plan_choices()

        if getattr(self, 'instance', None) and self.instance.pk:
            self.initial.setdefault('alojamientos', self.instance.alojamientos or [])
            self.initial.setdefault('actividades', self.instance.actividades or [])
            self.initial.setdefault('restaurantes', self.instance.restaurantes or [])
            self.initial.setdefault('planings', [str(p) for p in (self.instance.planings or [])])

    def save(self, commit=True):
        user = super().save(commit=False)
        user.alojamientos = self.cleaned_data.get('alojamientos', [])
        user.actividades = self.cleaned_data.get('actividades', [])
        user.restaurantes = self.cleaned_data.get('restaurantes', [])
        user.planings = self.cleaned_data.get('planings', [])
        if commit:
            user.save()
            self.save_m2m()
        return user


class CustomUserCreationForm(_ServiceFormMixin, UserCreationForm):
    alojamientos = ServiceMultipleChoiceField(
        choices=[],
        required=False,
        widget=TomSelectMultiple,
        label='Alojamientos',
    )
    actividades = ServiceMultipleChoiceField(
        choices=[],
        required=False,
        widget=TomSelectMultiple,
        label='Actividades',
    )
    restaurantes = ServiceMultipleChoiceField(
        choices=[],
        required=False,
        widget=TomSelectMultiple,
        label='Restaurantes',
    )
    planings = ServiceMultipleChoiceField(
        choices=[],
        required=False,
        widget=TomSelectMultiple,
        label='Plannings',
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
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
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_service_fields()


class CustomUserChangeForm(_ServiceFormMixin, UserChangeForm):
    alojamientos = ServiceMultipleChoiceField(
        choices=[],
        required=False,
        widget=TomSelectMultiple,
        label='Alojamientos',
    )
    actividades = ServiceMultipleChoiceField(
        choices=[],
        required=False,
        widget=TomSelectMultiple,
        label='Actividades',
    )
    restaurantes = ServiceMultipleChoiceField(
        choices=[],
        required=False,
        widget=TomSelectMultiple,
        label='Restaurantes',
    )
    planings = ServiceMultipleChoiceField(
        choices=[],
        required=False,
        widget=TomSelectMultiple,
        label='Plannings',
    )

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "seller",
            "alojamientos",
            "actividades",
            "restaurantes",
            "planings",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_service_fields()
