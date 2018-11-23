# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD 3-Clause License. Please seel the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

import sys

import requests
from django.utils.translation import gettext_lazy as _
from uwsgi_tasks import RetryTaskException, task

from generic.utils import TokenAuth, print_error, print_message, print_warning, retry_get


@task(retry_count=5, retry_timeout=300)
def remove_from_trillian(pk):
    from measurements.models import InstanceRun

    try:
        # Try to find the InstanceRun multiple times, in case of a race condition
        run = retry_get(InstanceRun.objects.exclude(analysed=None), pk=pk)

        if not run.analysed:
            print_warning(_("InstanceRun {pk} has not yet been analysed").format(pk=pk))
            return

        if not run.trillian_url:
            # Already cleaned up
            return

        print_message(_("Deleting InstanceRun {run.pk} ({run.url}) from {run.trillian.name}").format(run=run))

        response = requests.request(
            method='DELETE',
            url=run.trillian_url,
            auth=TokenAuth(run.trillian.token),
            timeout=(5, 15),
        )

        print(response)

        if response.status_code not in [204, 404]:
            # 204 = deleted, 404 = doesn't exist anymore
            print_error(
                _("{run.trillian.name} didn't accept our request ({response.status_code}), retrying later").format(
                    run=run,
                    response=response
                )
            )
            raise RetryTaskException

        run.trillian_url = ''
        run.save()

        print_message(_("Trillian {run.trillian.name} deleted completed InstanceRun {run.pk}").format(run=run))

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
