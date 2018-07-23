import sys

import requests
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from requests.auth import AuthBase
from uwsgi_tasks import RetryTaskException, task

from generic.utils import print_error, print_message, print_warning, retry_get


class TokenAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, req):
        req.headers['Authorization'] = 'Token {}'.format(self.token)
        return req


@task(retry_count=5, retry_timeout=300)
def delegate_to_trillian(pk):
    from measurements.models import InstanceRun

    try:
        # Try to find the InstanceRun multiple times, in case of a race condition
        run = retry_get(InstanceRun.objects.all(), pk=pk)

        if run.trillian_url:
            print_warning(_("Trillian URL already exists for InstanceRun {pk}").format(pk=pk))
            return

        print_message(_("Pushing InstanceRun {run.pk} ({run.url}) to {run.trillian.name}").format(run=run))

        if settings.ALLOWED_HOSTS:
            my_hostname = settings.ALLOWED_HOSTS[0]
        else:
            my_hostname = 'localhost'

        response = requests.request(
            method='POST',
            url='https://{hostname}/api/v1/instanceruns/'.format(hostname=run.trillian.hostname),
            auth=TokenAuth(run.trillian.token),
            timeout=(5, 15),
            json={
                'url': run.url,
                'callback_url': 'https://{my_hostname}{path}'.format(
                    my_hostname=my_hostname,
                    path=reverse('v1:instancerun-detail', kwargs={'pk': run.pk})
                ),
                'requested': run.testrun.requested.isoformat(),
            }
        )

        if response.status_code != 201:
            print_error(
                _("{run.trillian.name} didn't accept our request ({response.status_code}), retrying later").format(
                    run=run,
                    response=response
                )
            )
            raise RetryTaskException

        run.trillian_url = response.json()['_url']
        run.save()

        print_message(_("Trillian {run.trillian.name} accepted the task as {run.trillian_url}").format(run=run))

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
