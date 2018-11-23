# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

# Generated by Django 2.0.7 on 2018-07-09 12:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('measurements', '0002_rename_pings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instancerun',
            name='requested',
        ),
    ]
