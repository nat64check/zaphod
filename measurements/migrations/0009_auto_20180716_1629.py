# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

# Generated by Django 2.0.7 on 2018-07-16 16:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('measurements', '0008_trillian_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instancerun',
            name='trillian_url',
            field=models.URLField(blank=True, verbose_name='Trillian URL'),
        ),
    ]
