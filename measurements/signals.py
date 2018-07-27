from django.db.models.signals import post_save
from django.dispatch import receiver

from measurements.models import InstanceRun
from measurements.tasks import delegate_to_trillian


# noinspection PyUnusedLocal
@receiver(post_save, sender=InstanceRun, dispatch_uid='schedule_push')
def schedule_push(instance: InstanceRun, **kwargs):
    # Schedule push to Trillian in the spooler
    if instance.trillian_url:
        return

    delegate_to_trillian(instance.pk)


# noinspection PyUnusedLocal
@receiver(post_save, sender=InstanceRun, dispatch_uid='update_testrun_from_instancerun')
def update_testrun_from_instancerun(sender, instance: InstanceRun, **kwargs):
    updated = []
    if instance.started and (not instance.testrun.started or instance.testrun.started > instance.started):
        instance.testrun.started = instance.started
        updated.append('started')

    # Testrun finished depends on analysed of instanceruns
    finished = list(instance.testrun.instanceruns.values_list('analysed', flat=True))
    if all(finished):
        instance.testrun.finished = max(finished)
        updated.append('finished')

    if updated:
        instance.testrun.save(update_fields=updated)
