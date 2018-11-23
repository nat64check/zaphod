# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

# Generated by Django 2.0.7 on 2018-07-27 13:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('measurements', '0011_testrun_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='instancerunresult',
            name='analysed',
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                null=True,
                verbose_name='analysed'
            ),
        ),
        migrations.AddField(
            model_name='instancerunresult',
            name='image_feedback',
            field=models.TextField(
                blank=True,
                verbose_name='image feedback'
            ),
        ),
        migrations.AddField(
            model_name='instancerunresult',
            name='image_score',
            field=models.FloatField(
                blank=True,
                db_index=True,
                null=True,
                verbose_name='image score'
            ),
        ),
        migrations.AddField(
            model_name='instancerunresult',
            name='overall_feedback',
            field=models.TextField(
                blank=True,
                verbose_name='overall feedback'
            ),
        ),
        migrations.AddField(
            model_name='instancerunresult',
            name='overall_score',
            field=models.FloatField(
                blank=True,
                db_index=True,
                null=True,
                verbose_name='overall score'
            ),
        ),
        migrations.AddField(
            model_name='instancerunresult',
            name='resource_feedback',
            field=models.TextField(
                blank=True,
                verbose_name='resource feedback'
            ),
        ),
        migrations.AddField(
            model_name='instancerunresult',
            name='resource_score',
            field=models.FloatField(
                blank=True,
                db_index=True,
                null=True,
                verbose_name='resource score'
            ),
        ),
        migrations.AlterField(
            model_name='instancerunresult',
            name='when',
            field=models.DateTimeField(
                verbose_name='when'
            ),
        ),
    ]
