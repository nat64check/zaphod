from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from measurements.models import InstanceRun, InstanceRunResult, TestRun
from measurements.tasks import delegate_to_trillian


# noinspection PyUnusedLocal
@receiver(post_save, sender=InstanceRun, dispatch_uid='schedule_push')
def schedule_push(instance: InstanceRun, **kwargs):
    # Schedule push to Trillian in the spooler
    if instance.trillian_url:
        return

    delegate_to_trillian(instance.pk)


# noinspection PyUnusedLocal
@receiver(post_save, sender=InstanceRunResult, dispatch_uid='schedule_instancerunresult_analysis')
def schedule_instancerunresult_analysis(sender, instance: InstanceRunResult, **kwargs):
    # When finished has changed, or if it hasn't been analysed after X minutes
    if instance.tracker.has_changed('when') or instance.when < timezone.now() - timedelta(minutes=5):
        instance.trigger_analysis()


# noinspection PyUnusedLocal
@receiver(post_save, sender=InstanceRun, dispatch_uid='schedule_instancerun_analysis')
def schedule_instancerun_analysis(sender, instance: InstanceRun, **kwargs):
    if instance.tracker.has_changed('finished') or \
            (instance.finished and instance.finished < timezone.now() - timedelta(minutes=5)):
        instance.trigger_analysis()


# noinspection PyUnusedLocal
@receiver(post_save, sender=TestRun, dispatch_uid='schedule_testrun_analysis')
def schedule_testrun_analysis(sender, instance: TestRun, **kwargs):
    if instance.tracker.has_changed('finished') or \
            (instance.finished and instance.finished < timezone.now() - timedelta(minutes=5)):
        instance.trigger_analysis()


# noinspection PyUnusedLocal
@receiver(post_save, sender=InstanceRun, dispatch_uid='update_testrun_from_instancerun')
def update_testrun_from_instancerun(sender, instance: InstanceRun, **kwargs):
    updated = []
    if instance.started and (not instance.testrun.started or instance.testrun.started > instance.started):
        instance.testrun.started = instance.started
        updated.append('started')

    finished = list(instance.testrun.instanceruns.values_list('finished', flat=True))
    if all(finished):
        instance.testrun.finished = max(finished)
        updated.append('finished')

    if updated:
        instance.testrun.save(update_fields=updated)
