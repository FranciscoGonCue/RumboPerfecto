from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import PlanViaje


@receiver(post_save, sender=PlanViaje)
def add_plan_to_user(sender, instance, created, **kwargs):
    if not created or not instance.usuario_id:
        return
    user = instance.usuario
    planings = list(user.planings or [])
    plan_id = str(instance.id_plan)
    if plan_id not in planings:
        planings.append(plan_id)
        user.planings = planings
        user.save(update_fields=['planings'])


@receiver(post_delete, sender=PlanViaje)
def remove_plan_from_user(sender, instance, **kwargs):
    if not instance.usuario_id:
        return
    user = instance.usuario
    plan_id = str(instance.id_plan)
    planings = [p for p in (user.planings or []) if str(p) != plan_id]
    user.planings = planings
    user.save(update_fields=['planings'])
