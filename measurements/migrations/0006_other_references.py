# Generated by Django 2.0rc1 on 2017-11-25 19:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('measurements', '0005_instanceruns_reference'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instancerunresult',
            name='instancerun',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results',
                                    to='measurements.InstanceRun', verbose_name='instancerun'),
        ),
        migrations.AlterField(
            model_name='testrun',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='testruns', to=settings.AUTH_USER_MODEL, verbose_name='owner'),
        ),
        migrations.AlterField(
            model_name='testrun',
            name='schedule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='testruns', to='measurements.Schedule', verbose_name='schedule'),
        ),
    ]
