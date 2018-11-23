# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

# Generated by Django 2.0.7 on 2018-07-09 12:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('measurements', '0003_remove_instancerun_requested'),
    ]

    operations = [
        migrations.AddField(
            model_name='instancerun',
            name='analysed',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='analysed'),
        ),
        migrations.AddField(
            model_name='testrun',
            name='analysed',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='analysed'),
        ),
    ]
