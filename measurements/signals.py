from django.db.models.signals import post_save
from django.dispatch import receiver

from measurements.models import InstanceRun
from measurements.tasks import delegate_to_trillian


# noinspection PyUnusedLocal
@receiver(post_save, sender=InstanceRun, dispatch_uid='schedule_updater')
def schedule_push(instance: InstanceRun, **kwargs):
    # Schedule push to Trillian in the spooler
    if instance.trillian_url:
        return

    delegate_to_trillian(instance.pk)
