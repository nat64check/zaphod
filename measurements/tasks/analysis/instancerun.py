# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD 3-Clause License. Please seel the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

import sys
from statistics import mean

from django.db.transaction import atomic
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from uwsgi_tasks import RetryTaskException, task

from generic.utils import print_error, print_notice, print_warning, retry_all


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
        if run.analysed or not run.finished:
            return

        print_notice(_("Analysing InstanceRun {run.pk} ({run.url}) on {run.trillian.name}").format(run=run))

        scores = InstanceRunResult.objects \
            .filter(instancerun_id=pk) \
            .values_list('image_score', 'resource_score', 'overall_score')

        run.image_score = mean([score[0] for score in scores])
        run.resource_score = mean([score[1] for score in scores])
        run.overall_score = mean([score[2] for score in scores])

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
