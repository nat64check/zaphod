import sys
from statistics import mean

from django.db.transaction import atomic
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from uwsgi_tasks import RetryTaskException, task

from generic.utils import print_error, print_notice, print_warning, retry_all


@task(retry_count=3, retry_timeout=15)
@atomic
def analyse_instancerunresult(pk):
    from measurements.models import InstanceRunResult
    from measurements.utils import compare_base64_images

    try:
        result = InstanceRunResult.objects.select_for_update().get(pk=pk)
        if result.analysed:
            return

        print_notice(_("Analysing InstanceRunResult {result.pk} ({result.instance_type}: {result.instancerun.url}) "
                       "on {result.instancerun.trillian.name}").format(result=result))

        baseline = result.instancerun.get_baseline()
        if not baseline:
            result.image_score = 0
            result.resource_score = 0
            result.overall_score = 0
            result.analysed = timezone.now()
            result.save()
            return

        # If we have multiple possible combinations then test them all and choose the most positive one
        result.image_score = max([compare_base64_images(base.web_response['image'], result.web_response['image'])
                                  for base in baseline])
        result.analysed = timezone.now()
        result.save()

    except RetryTaskException:
        raise

    except InstanceRunResult.DoesNotExist:
        print_warning(_("InstanceRunResult {pk} does not exist anymore").format(pk=pk))
        return

    except Exception as ex:
        print_error(_('{name} on line {line}: {msg}').format(
            name=type(ex).__name__,
            line=sys.exc_info()[-1].tb_lineno,
            msg=ex
        ))

        raise RetryTaskException


@task(retry_count=3, retry_timeout=15)
@atomic
def analyse_instancerun(pk):
    from measurements.models import InstanceRun, InstanceRunResult

    try:
        children_finished = retry_all(InstanceRunResult.objects
                                      .filter(instancerun_id=pk)
                                      .values_list('analysed', flat=True))
        if not children_finished:
            return

        run = InstanceRun.objects.select_for_update().get(pk=pk)
        if run.analysed:
            return

        print_notice(_("Analysing InstanceRun {run.pk} ({run.url}) on {run.trillian.name}").format(run=run))

        run.image_score = mean(InstanceRunResult.objects
                               .filter(instancerun_id=pk)
                               .values_list('image_score', flat=True))
        run.analysed = timezone.now()
        run.save()

    except RetryTaskException:
        raise

    except InstanceRun.DoesNotExist:
        print_warning(_("InstanceRun {pk} does not exist anymore").format(pk=pk))
        return

    except Exception as ex:
        print_error(_('{name} on line {line}: {msg}').format(
            name=type(ex).__name__,
            line=sys.exc_info()[-1].tb_lineno,
            msg=ex
        ))

        raise RetryTaskException


@task(retry_count=3, retry_timeout=15)
@atomic
def analyse_testrun(pk):
    from measurements.models import TestRun, InstanceRun

    try:
        children_finished = retry_all(InstanceRun.objects
                                      .filter(testrun_id=pk)
                                      .values_list('analysed', flat=True))
        if not children_finished:
            return

        run = TestRun.objects.select_for_update().get(pk=pk)
        if run.analysed:
            return

        print_notice(_("Analysing TestRun {run.pk} ({run.url})").format(run=run))

        run.image_score = mean(InstanceRun.objects
                               .filter(testrun_id=pk)
                               .values_list('image_score', flat=True))
        run.analysed = timezone.now()
        run.save()

    except RetryTaskException:
        raise

    except TestRun.DoesNotExist:
        print_warning(_("TestRun {pk} does not exist anymore").format(pk=pk))
        return

    except Exception as ex:
        print_error(_('{name} on line {line}: {msg}').format(
            name=type(ex).__name__,
            line=sys.exc_info()[-1].tb_lineno,
            msg=ex
        ))

        raise RetryTaskException
