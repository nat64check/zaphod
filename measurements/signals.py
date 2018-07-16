from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from measurements.models import InstanceRun
from measurements.tasks import delegate_to_trillian


# noinspection PyUnusedLocal
@receiver(post_save, sender=InstanceRun, dispatch_uid='schedule_updater')
def schedule_push(instance: InstanceRun, **kwargs):
    # Schedule push to Trillian in the spooler
    if instance.trillian_url:
        return

    delegate_to_trillian.setup['at'] = timezone.now() + timedelta(seconds=1)
    delegate_to_trillian(instance.pk)
