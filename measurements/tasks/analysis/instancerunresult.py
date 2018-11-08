import sys

from django.db.transaction import atomic
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from uwsgi_tasks import RetryTaskException, task

from generic.utils import print_error, print_notice, print_warning, retry_get
from measurements.utils import get_resource_stats


@task(retry_count=3, retry_timeout=15)
@atomic
def analyse_instancerunresult(pk):
    from measurements.models import InstanceRunResult
    from measurements.utils import compare_base64_images

    try:
        result = retry_get(InstanceRunResult.objects.select_for_update(), pk=pk)
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
        result.image_score, base = max([(compare_base64_images(base.web_response['image'],
                                                               result.web_response['image']),
                                         base)
                                        for base in baseline])

        # Analyse the resources
        base_stats = get_resource_stats(base.web_response['resources'])
        my_stats = get_resource_stats(result.web_response['resources'])
        result.resource_score = min(1.0, my_stats['total']['ok'] / (base_stats['total']['ok'] or 1))

        # Determine the overall score
        result.overall_score = result.image_score * result.resource_score

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
