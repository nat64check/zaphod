# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD 3-Clause License. Please seel the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

import sys
from statistics import mean

from django.db.models import Avg
from django.db.transaction import atomic
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from uwsgi_tasks import RetryTaskException, task

from generic.utils import print_error, print_notice, print_warning, retry_all


@task(retry_count=3, retry_timeout=15)
@atomic
def analyse_testrun(pk):
    from measurements.models import (TestRun, InstanceRun, InstanceRunResult,
                                     TestRunAverage)

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

        scores = InstanceRun.objects \
            .filter(testrun_id=pk) \
            .values_list('image_score', 'resource_score', 'overall_score')

        run.image_score = mean([score[0] for score in scores])
        run.resource_score = mean([score[1] for score in scores])
        run.overall_score = mean([score[2] for score in scores])

        averages = InstanceRunResult.objects \
            .filter(instancerun__testrun_id=pk) \
            .values('marvin__instance_type') \
            .annotate(image_score=Avg('image_score'),
                      resource_score=Avg('resource_score'),
                      overall_score=Avg('overall_score'))

        for average in averages:
            TestRunAverage.objects.update_or_create(defaults={
                'image_score': average['image_score'],
                'resource_score': average['resource_score'],
                'overall_score': average['overall_score'],
            }, testrun_id=pk, instance_type=average['marvin__instance_type'])

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
